"""Encrypt a Model Room credential for the current Windows user with DPAPI."""

import ctypes
import os
import tempfile
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
        return _dpapi(path.read_bytes(), protect=False).decode("utf-8")
    except (OSError, UnicodeError):
        return ""


def write_secret(path: Path, key: str) -> None:
    protected = _dpapi(key.encode("utf-8"), protect=True)
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
