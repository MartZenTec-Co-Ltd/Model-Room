# Contributing

Model Room v1.0 currently ships **Windows x64 only**. Linux/macOS release builds are not provided.

1. Use a Windows x64 Python installation with Tkinter. The public EXE does not require Python installation; this requirement applies only to source development.
2. Install `requirements.txt`, then run `python model_room.py`.
3. Keep code, `translations.json`, and all five README files consistent. `room_version.py` is the application version source.
4. Use temporary `MODELROOM_DATA_DIR` folders for tests. Do not include real chats, photos, API keys or account state in fixtures or pull requests.
5. Run relevant scripts in `tests/`. The GUI checks require an interactive Windows desktop. `tests/check_lan_profile.mjs` can be run with Node.js and does not access the network.
6. Build with `build-windows.ps1`, or generate distributable assets with `release-windows.ps1`.

The Windows build workflow builds and checks the standalone executable. It uploads an Actions artifact; it does not publish a GitHub Release automatically.
Use GitHub Issues for reproducible bugs, omitting tokens, private transcripts and personal image paths. Open pull requests for source changes.

Application contributions are provided under the project MIT license. Third-party components retain their own terms in `THIRD_PARTY_NOTICES.md`.
