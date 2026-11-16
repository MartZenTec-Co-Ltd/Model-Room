# Model Room v1.1

- Windows x64 EXE; Linux x86_64 AppImage and DEB; macOS 15+ arm64 and Intel app/ZIP/DMG.
- Per-room, per-seat Markdown personality editor in Settings. Direct editing, templates, UTF-8 import/export, Apply/OK/Cancel.
- Personality reaches API, Codex, Claude Code and Harness requests in ordinary messages and discussions.
- Three-member offline adapter tests verify peer replies, human interruption, independent personalities and failure isolation. These are fixtures, not claims of paid-provider compatibility testing.
- Native directory opening, agent PATH discovery, child-process library cleanup, Unix credential storage and Linux/macOS scrolling.
- Five-language guides and personality documentation. Existing Windows v1.0 data remains compatible.

## Platform boundaries

Linux targets x86_64, glibc 2.35+, X11/XWayland. Native CI builds on Ubuntu 22.04 and runs packaged diagnostics there and in Kali Rolling. Test status is established by the matching GitHub Actions run, not by this list of workflow steps.

macOS targets macOS 15+ with separate Apple Silicon and Intel builds. Ad-hoc signatures are checked, but no Developer ID or Apple notarization is included. Gatekeeper may require a user trust decision. No security system is disabled.

All binaries include Python and GUI/image dependencies. Optional model agents and provider accounts are separate. No API keys, user databases or private photos are bundled. See SHA256SUMS for release file integrity.
