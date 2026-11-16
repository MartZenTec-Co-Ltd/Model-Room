"""Small native desktop integration helpers, shared by all release formats."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

_fontconfig = Path(__file__).parent/'packaging/fontconfig-modelroom.conf'
_fontconfig_override = sys.platform == 'linux' and not os.environ.get('FONTCONFIG_FILE') and _fontconfig.is_file()
if _fontconfig_override:
    # Process-local: never alter a user's desktop font configuration.
    os.environ['FONTCONFIG_FILE'] = str(_fontconfig)


def child_environment():
    env = os.environ.copy()
    if _fontconfig_override and env.get('FONTCONFIG_FILE') == str(_fontconfig):
        env.pop('FONTCONFIG_FILE',None)
    if getattr(sys, 'frozen', False):
        for name in ('LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH'):
            original = env.get(name+'_ORIG')
            if original is None:
                env.pop(name, None)
            else:
                env[name] = original
        for name in ('TCL_LIBRARY','TK_LIBRARY','PYTHONHOME','PYTHONPATH'):
            env.pop(name, None)
    # Finder launches apps with a minimal PATH. Include conventional CLI install paths.
    if os.name != 'nt':
        paths = [str(Path.home()/'.local/bin'), '/opt/homebrew/bin', '/usr/local/bin',
                 *env.get('PATH','').split(os.pathsep), '/usr/bin', '/bin']
        env['PATH'] = os.pathsep.join(dict.fromkeys(p for p in paths if p))
    return env


def find_program(name):
    return shutil.which(name, path=child_environment().get('PATH'))


def open_directory(directory):
    path = Path(directory).expanduser().resolve(strict=True)
    if not path.is_dir():
        raise OSError('Not a directory')
    if os.name == 'nt':
        os.startfile(str(path))
    else:
        command = 'open' if sys.platform == 'darwin' else 'xdg-open'
        subprocess.Popen([command, str(path)], env=child_environment(),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
