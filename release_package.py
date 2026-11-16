"""Create public standalone/source assets; never collect user data directories."""
import argparse
import ast
import hashlib
import json
import platform
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from room_version import VERSION


def public_files(source):
    root_names = {"LICENSE", "THIRD_PARTY_NOTICES.md", "CHANGELOG.md", "CONTRIBUTING.md", "RELEASE_NOTES.md",
                  ".gitignore", ".gitattributes", "ModelRoom.ico", "translations.json", "lan_room.html", "requirements.txt", "requirements-build.txt"}
    for path in sorted(source.iterdir()):
        if path.is_file() and (path.name in root_names or path.suffix in {".py", ".ps1", ".cs"} or path.name.startswith(("README", "PERSONALITIES"))):
            yield path
    for name in (".github", "licenses", "examples", "tests", "packaging"):
        for path in sorted((source/name).rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if name == "licenses" or (name == "tests" and path.suffix in {".py", ".mjs"}) or (name in {"examples","packaging"} and path.suffix in {".json", ".md", ".conf"}) or (name == ".github" and path.suffix in {".yml", ".yaml", ".md"}):
                yield path


def package(source, executable, output):
    source, executable, output = source.resolve(), executable.resolve(), output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    files = list(public_files(source))
    assert len(list(source.glob("README*.md"))) == 5
    for path in files:
        assert path.suffix.lower() not in {".db", ".sqlite3", ".key", ".pem", ".env"}, path
        if path.suffix == ".py":
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    filename = f"ModelRoom-v{VERSION}-Windows-x64.exe"
    target = output/filename
    if executable != target:
        shutil.copyfile(executable, target)
    source_zip = output/f"ModelRoom-v{VERSION}-Source.zip"
    with ZipFile(source_zip, "w", ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, f"ModelRoom-v{VERSION}/"+path.relative_to(source).as_posix())
    windows_zip = output/f"ModelRoom-v{VERSION}-Windows-x64.zip"
    with ZipFile(windows_zip, "w", ZIP_DEFLATED) as archive:
        archive.write(target, filename)
        for path in source.glob("README*.md"):
            archive.write(path, path.name)
        for path in source.glob('PERSONALITIES*.md'):
            archive.write(path,path.name)
        for path in (source/'examples/personalities').glob('*.md'):
            archive.write(path,'examples/personalities/'+path.name)
        for name in ("LICENSE", "THIRD_PARTY_NOTICES.md", "RELEASE_NOTES.md"):
            archive.write(source/name, name)
        for path in (source/"licenses").rglob("*"):
            if path.is_file():
                archive.write(path, "licenses/"+path.relative_to(source/"licenses").as_posix())
    import PIL
    info = output/f"ModelRoom-v{VERSION}-BuildInfo.json"
    info.write_text(json.dumps({"application":"Model Room", "version":VERSION, "platform":"Windows",
        "architecture":"x64", "python_runtime":platform.python_version(), "pillow":PIL.__version__,
        "self_contained":True, "requires_python_install":False, "license":"MIT"}, indent=2)+"\n", encoding="utf-8")
    artifacts = [target, windows_zip, source_zip, info]
    sums = output/f"SHA256SUMS-v{VERSION}.txt"
    sums.write_text("".join(hashlib.sha256(path.read_bytes()).hexdigest()+"  "+path.name+"\n" for path in artifacts),encoding="utf-8")
    return artifacts+[sums]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("release"))
    args = parser.parse_args()
    for path in package(Path(__file__).resolve().parent, args.exe, args.output):
        print(path)
