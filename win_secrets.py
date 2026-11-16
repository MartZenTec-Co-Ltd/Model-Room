"""DPAPI on Windows; authenticated encryption and private files on Unix.

The Unix vault key is a local mode-0600 file, not an OS keychain or a password
vault. Protect the entire user data directory when making backups.
"""

import ctypes
import os
import tempfile
import stat
from ctypes import wintypes
from pathlib import Path


class _Blob(ctypes.Structure):
    _fields_ = [("size", wintypes.DWORD), ("data", ctypes.c_void_p)]


def _dpapi(data: bytes, protect: bool) -> bytes:
    buffer = ctypes.create_string_buffer(data)
    source = _Blob(len(data), ctypes.cast(buffer, ctypes.c_void_p))
    result = _Blob()
    crypt = ctypes.WinDLL("crypt32", use_last_error=True)
    free = ctypes.WinDLL("kernel32").LocalFree
    free.argtypes = [ctypes.c_void_p]
    free.restype = ctypes.c_void_p
    operation = crypt.CryptProtectData if protect else crypt.CryptUnprotectData
    operation.argtypes = [
        ctypes.POINTER(_Blob), ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(_Blob),
    ]
    operation.restype = wintypes.BOOL
    if not operation(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(result)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return ctypes.string_at(result.data, result.size)
    finally:
        free(result.data)


def read_secret(path: Path) -> str:
    try:
        if os.name == 'nt':
            return _dpapi(path.read_bytes(), protect=False).decode("utf-8")
        if not path.exists():
            return ''
        from cryptography.fernet import Fernet, InvalidToken
        try:
            content = _private_read(path)
            if not content.startswith(b'MODELROOM-FERNET-1\n'):
                return ''
            return Fernet(_vault_key(path.parent, create=False)).decrypt(content.split(b'\n',1)[1]).decode('utf-8')
        except (InvalidToken, ValueError):
            return ''
    except (OSError, UnicodeError):
        return ""


def write_secret(path: Path, key: str) -> None:
    if os.name == 'nt':
        protected = _dpapi(key.encode("utf-8"), protect=True)
    else:
        from cryptography.fernet import Fernet
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if path.parent.is_symlink() or path.parent.stat().st_uid != os.getuid():
            raise OSError('Credential directory must belong to the current user.')
        os.chmod(path.parent, 0o700)
        protected = b'MODELROOM-FERNET-1\n' + Fernet(_vault_key(path.parent, create=True)).encrypt(key.encode('utf-8'))
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as staged:
        temp = Path(staged.name)
        try:
            staged.write(protected)
            staged.close()
            os.replace(temp, path)
        finally:
            staged.close()
            temp.unlink(missing_ok=True)


def _private_read(path):
    descriptor = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    with os.fdopen(descriptor, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise OSError('Credential files must be owned by the current user with mode 0600.')
        return stream.read(128 * 1024)


def _vault_key(directory, *, create):
    path = directory / '.modelroom-vault-key'
    if create:
        try:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            from cryptography.fernet import Fernet
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(Fernet.generate_key())
                stream.flush()
                os.fsync(stream.fileno())
    return _private_read(path)
