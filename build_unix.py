"""Build self-contained Linux AppImage/DEB or macOS app/DMG on the native OS."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import plistlib
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from room_version import VERSION

ROOT = Path(__file__).resolve().parent


def run(*args, **kwargs):
    subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def download(url, digest, path):
    request = urllib.request.Request(url, headers={'User-Agent':'ModelRoom-build'})
    with urllib.request.urlopen(request, timeout=120) as response, path.open('wb') as output:
        shutil.copyfileobj(response, output)
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise RuntimeError('Build tool SHA256 mismatch; review and update its pin before executing.')
    path.chmod(0o755)


def desktop(exec_path='ModelRoom'):
    return ('[Desktop Entry]\nType=Application\nName=Model Room\n'
            'Comment=Group chat for people and multiple AI models\n'
            f'Exec={exec_path}\nIcon=modelroom\nTerminal=false\nCategories=Utility;\n')


def build(target):
    if (target == 'linux' and sys.platform != 'linux') or (target == 'macos' and sys.platform != 'darwin'):
        raise SystemExit('Run this builder on the native target OS; it is not a cross compiler.')
    release = ROOT/'release'
    release.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='modelroom-build-') as temp:
        temp = Path(temp)
        from PIL import Image
        icon = Image.open(ROOT/'ModelRoom.ico').convert('RGBA')
        icon.resize((256,256)).save(temp/'modelroom.png')
        command = [sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onedir',
                   '--name','ModelRoom','--distpath',str(temp/'dist'),'--workpath',str(temp/'work'),
                   '--specpath',str(temp),'--paths',str(ROOT),'--hidden-import','room_selftest',
                   '--collect-all','certifi','--collect-all','cryptography',
                   '--copy-metadata','Pillow','--copy-metadata','cryptography']
        resources = ['translations.json','lan_room.html','licenses','LICENSE','THIRD_PARTY_NOTICES.md',
                     *[p.name for p in ROOT.glob('README*.md')],
                     *[p.name for p in ROOT.glob('PERSONALITIES*.md')], 'examples']
        for name in resources:
            destination = name if (ROOT/name).is_dir() else '.'
            command += ['--add-data',str(ROOT/name)+os.pathsep+destination]
        if target == 'macos':
            icon.resize((1024,1024)).save(temp/'ModelRoom.icns',format='ICNS')
            command += ['--windowed','--icon',str(temp/'ModelRoom.icns'),
                        '--osx-bundle-identifier','io.github.martzentec.modelroom']
        command += [str(ROOT/'model_room.py')]
        run(*command,cwd=ROOT)
        if target == 'linux':
            if platform.machine().lower() not in {'x86_64','amd64'}:
                raise SystemExit('This Linux release targets x86_64.')
            appdir = temp/'ModelRoom.AppDir'
            (appdir/'usr/lib').mkdir(parents=True)
            shutil.copytree(temp/'dist/ModelRoom',appdir/'usr/lib/modelroom',symlinks=True)
            shutil.copy2(temp/'modelroom.png',appdir/'modelroom.png')
            (appdir/'modelroom.desktop').write_text(desktop())
            apprun = appdir/'AppRun'
            apprun.write_text('#!/bin/sh\nHERE="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"\nexec "$HERE/usr/lib/modelroom/ModelRoom" "$@"\n')
            apprun.chmod(0o755)
            tools = temp/'tools'
            tools.mkdir()
            pins = json.loads((ROOT/'packaging/appimage-tools.json').read_text())
            for name, info in pins.items():
                download(info['url'],info['sha256'],tools/name)
            env = os.environ.copy()
            env.update(ARCH='x86_64',APPIMAGE_EXTRACT_AND_RUN='1',SOURCE_DATE_EPOCH='1794787200')
            run(tools/'appimagetool', '--runtime-file',tools/'runtime',appdir,
                release/f'ModelRoom-v{VERSION}-Linux-x86_64.AppImage',env=env)
            deb = temp/'deb'
            (deb/'opt').mkdir(parents=True)
            shutil.copytree(temp/'dist/ModelRoom',deb/'opt/modelroom',symlinks=True)
            (deb/'usr/bin').mkdir(parents=True)
            launcher = deb/'usr/bin/modelroom'
            launcher.write_text('#!/bin/sh\nexec /opt/modelroom/ModelRoom "$@"\n')
            launcher.chmod(0o755)
            (deb/'usr/share/applications').mkdir(parents=True)
            (deb/'usr/share/applications/modelroom.desktop').write_text(desktop('modelroom'))
            (deb/'usr/share/icons/hicolor/256x256/apps').mkdir(parents=True)
            shutil.copy2(temp/'modelroom.png',deb/'usr/share/icons/hicolor/256x256/apps/modelroom.png')
            docs = deb/'usr/share/doc/model-room'
            docs.mkdir(parents=True)
            for name in resources:
                if (ROOT/name).is_file():
                    shutil.copy2(ROOT/name,docs/name)
            (deb/'DEBIAN').mkdir()
            (deb/'DEBIAN/control').write_text(
                f'Package: model-room\nVersion: {VERSION}\nSection: utils\nPriority: optional\nArchitecture: amd64\n'
                'Maintainer: MartZenTec.Co., Ltd\n'
                'Depends: libc6 (>= 2.35), libx11-6, libxext6, libxrender1, libxft2, libfontconfig1, libxss1, libxcb1, zlib1g\n'
                'Homepage: https://github.com/MartZenTec-Co-Ltd/Model-Room\n'
                'Description: Group chat for people and multiple AI models\n'
                ' Includes Python, Tcl/Tk, Pillow and the application runtime.\n')
            run('dpkg-deb','--root-owner-group','--build',deb,release/f'model-room_{VERSION}_amd64.deb')
            arch, minimum = 'x86_64','glibc 2.35; desktop X11 or XWayland'
        else:
            arch = 'arm64' if platform.machine().lower() == 'arm64' else 'x86_64'
            app = temp/'dist/ModelRoom.app'
            plist = app/'Contents/Info.plist'
            data = plistlib.loads(plist.read_bytes())
            data.update(CFBundleShortVersionString=VERSION,CFBundleVersion=VERSION,LSMinimumSystemVersion='15.0',
                        NSHighResolutionCapable=True,NSHumanReadableCopyright='MIT · MartZenTec.Co., Ltd')
            plist.write_bytes(plistlib.dumps(data))
            run('codesign','--force','--deep','--sign','-',app)
            run('codesign','--verify','--deep','--strict',app)
            run('ditto','-c','-k','--sequesterRsrc','--keepParent',app,
                release/f'ModelRoom-v{VERSION}-macOS-{arch}.zip')
            dmg = temp/'dmg'
            dmg.mkdir()
            shutil.copytree(app,dmg/'ModelRoom.app',symlinks=True)
            (dmg/'Applications').symlink_to('/Applications',target_is_directory=True)
            run('hdiutil','create','-volname','Model Room','-srcfolder',dmg,'-ov','-format','UDZO',
                release/f'ModelRoom-v{VERSION}-macOS-{arch}.dmg')
            minimum = 'macOS 15; ad-hoc signed, not Apple notarized'
        import PIL
        info = {'application':'Model Room','version':VERSION,'platform':target,'architecture':arch,
                'python_runtime':platform.python_version(),'pillow':PIL.__version__,'self_contained':True,
                'requires_python_install':False,'minimum_environment':minimum,'license':'MIT',
                'apple_notarized':False if target == 'macos' else None}
        (release/f'ModelRoom-v{VERSION}-{target}-{arch}-BuildInfo.json').write_text(json.dumps(info,indent=2)+'\n')


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('platform',choices=['linux','macos'])
    build(parser.parse_args().platform)
