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
