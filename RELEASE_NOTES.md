# Model Room v1.0 — public Windows release

**Release date:** 2026-11-12 · **Platform:** Windows 10/11 x64 · **License:** MIT

## Download

- **ModelRoom-v1.0-Windows-x64.exe** — ordinary users: download and double-click. No Python, pip, Tkinter or Pillow installation is needed.
- **ModelRoom-v1.0-Windows-x64.zip** — the same EXE plus all five guides and license notices.
- **ModelRoom-v1.0-Source.zip** — source for developers and GitHub publication; not the runnable app download.
- **SHA256SUMS-v1.0.txt** — SHA-256 checksums for the three assets and build information.
- **ModelRoom-v1.0-BuildInfo.json** — public version/architecture/runtime information; contains no personal data.

The EXE carries its runtime inside the file and extracts a private cache into `%LOCALAPPDATA%\ModelRoom\runtime` on first launch. It does not search PATH for Python or download/install Python. Saved rooms and preferences live under `%LOCALAPPDATA%\ModelRoom`.

AI model weights, API accounts and optional local agents are not included. Configure your own provider or supported installed agent. No Linux or macOS binary is provided in this release.

## Publishing on GitHub

1. Upload the contents of the prepared source folder to the repository root. Keep `LICENSE`, `.gitignore`, `.github`, `licenses`, and the five README files.
2. Create a release tagged **v1.0** and attach the EXE, Windows ZIP, Source ZIP, checksums and build information listed above.
3. Copy the release description from this file, or use the desired language's README introduction.
4. Do not upload `%LOCALAPPDATA%\ModelRoom`, private `work` folders, chat databases, API keys or personal images.

The included GitHub Actions workflow builds/checks an EXE and uploads a workflow artifact. Publication of a public Release remains an explicit repository-owner action.

## Offline diagnostic (maintainers)

Run `ModelRoom-v1.0-Windows-x64.exe --self-test report.json` and wait for the process to finish. The report checks the embedded runtime, GUI, image rendering and settings using temporary fixtures, without requesting AI replies or reading personal chats.
