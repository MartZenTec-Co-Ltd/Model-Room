# Third-party notices

Model Room's application code and documentation use the project license in `LICENSE`.
Bundled third-party software keeps its own copyright and license terms.

- **CPython and its standard library**: Python Software Foundation and historical license terms. See `licenses/Python-LICENSE.txt`; the extracted EXE runtime also retains the distribution's `LICENSE.txt` and component notices.
- **Tcl/Tk**: copyright and redistribution notices are retained in the bundled Tcl/Tk files. See `licenses/Tk-license.terms` and `licenses/Tcl-license.terms`.
- **Pillow and its bundled imaging components**: see `licenses/Pillow-LICENSE.txt` and the bundled `pillow-*.dist-info/licenses/` directory in the extracted runtime.
- **Windows system libraries and .NET Framework**: supplied by Windows; the application does not bundle a separate .NET installer.

The EXE embeds a complete application runtime and extracts it locally on first launch.
End users do not need to install Python, Tkinter, Pillow or pip.
Cloud model providers and optional local agents are external services/tools with their own terms and authentication.


## v1.1 native packages

Linux and macOS packages use [PyInstaller](https://pyinstaller.org/) (GPL with its bootloader exception), [cryptography](https://cryptography.io/) (Apache-2.0 / BSD-3-Clause), and [certifi](https://github.com/certifi/python-certifi) / Mozilla CA data (MPL-2.0). Package metadata/licenses and collected dependency notices accompany their runtime files. Cryptography's native wheel also contains OpenSSL, with its own notices.

AppImage tooling: [appimagetool](https://github.com/AppImage/appimagetool) and [type2-runtime](https://github.com/AppImage/type2-runtime). Tool downloads are SHA256-pinned in packaging/appimage-tools.json; a changed upstream continuous build fails verification until the pins are reviewed.
