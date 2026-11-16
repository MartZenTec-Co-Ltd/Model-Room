"""Bundle the installed x64 Windows Python runtime and the application."""

import platform
import sys
import tkinter
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def write_runtime(target: Path) -> None:
    if sys.platform != "win32" or platform.machine().lower() not in {"amd64", "x86_64"}:
        raise SystemExit("Build this package with 64-bit x86 Python for Windows.")
    if sys.version_info < (3, 10) or not tkinter.TkVersion:
        raise SystemExit("Python 3.10 or newer with Tkinter is required.")

    runtime = Path(sys.base_prefix)
    source = Path(__file__).resolve().parent
    directories = ("Lib", "DLLs", "tcl")
    excluded = {"site-packages", "__pycache__", "test", "tests", "ensurepip", "idlelib"}
    if not (runtime / "pythonw.exe").is_file() or not all((runtime / name).is_dir() for name in directories):
        raise SystemExit("Use a full Windows Python installation with Tcl/Tk.")

    with ZipFile(target, "w", ZIP_DEFLATED, compresslevel=6) as bundle:
        for path in sorted(runtime.iterdir()):
            if path.is_file() and (path.suffix.lower() == ".dll" or path.name.lower() in {
                "pythonw.exe", "license.txt",
            }):
                bundle.write(path, path.name)
        for name in directories:
            for path in sorted((runtime / name).rglob("*")):
                relative = path.relative_to(runtime)
                if path.is_file() and not excluded.intersection(relative.parts):
                    bundle.write(path, relative.as_posix())
        for name in ("model_room.py", "room_core.py", "room_providers.py", "room_search.py", "room_settings.py",
                     "room_group.py", "room_members.py", "room_lan.py", "room_lan_ui.py", "lan_room.html",
                     "win_secrets.py", "room_style.py", "room_export.py", "room_presets.py", "room_claude.py",
                     "room_agents.py", "room_locale.py", "room_preferences.py", "room_settings_hub.py", "room_controls.py",
                     "room_identity.py", "room_wallpaper.py",
                     "room_version.py", "room_selftest.py", "room_platform.py", "room_personality.py", "room_personality_ui.py",
                     "translations.json", "ModelRoom.ico"):
            bundle.write(source / name, "Lib/" + name)
        for path in (source / "licenses").rglob("*"):
            if path.is_file():
                bundle.write(path, "licenses/" + path.relative_to(source / "licenses").as_posix())
        for path in (source/'examples/personalities').glob('*.md'):
            bundle.write(path,'Lib/examples/personalities/'+path.name)
        for name in ("LICENSE", "THIRD_PARTY_NOTICES.md"):
            if (source / name).is_file():
                bundle.write(source / name, name)
        import PIL
        pillow = Path(PIL.__file__).resolve().parent
        for path in sorted(pillow.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                bundle.write(path, "Lib/PIL/" + path.relative_to(pillow).as_posix())
        for metadata in pillow.parent.glob("pillow-*.dist-info"):
            for path in metadata.rglob("*"):
                if path.is_file():
                    bundle.write(path, "Lib/" + path.relative_to(pillow.parent).as_posix())
        import certifi
        certificates = Path(certifi.__file__).parent
        for path in certificates.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                bundle.write(path,'Lib/certifi/'+path.relative_to(certificates).as_posix())


if __name__ == "__main__":
    write_runtime(Path(sys.argv[1]))
