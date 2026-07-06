# Installing TrendForge AI (Windows)

TrendForge AI ships as a single Windows installer. You do **not** need Python,
Node.js, or any terminal — everything is bundled.

## Install

1. Download `TrendForge-AI-<version>-setup.exe`.
2. (Optional) verify the download against `SHA256SUMS.txt`:
   ```powershell
   Get-FileHash .\TrendForge-AI-<version>-setup.exe -Algorithm SHA256
   ```
3. Run the installer and click **Next → Next → Finish**.
   - Choose the install directory (or accept the default).
   - Desktop and Start Menu shortcuts are created automatically.
4. Launch **TrendForge AI** from the Desktop or Start Menu.

On first launch the app automatically creates its workspace, initializes the
database, applies migrations, and opens a short onboarding wizard.

## Enable AI features

Collection, research, timelines and analytics work immediately. To unlock AI
analysis and content generation, open **Settings → AI Provider**, paste an API
key (Gemini, OpenAI, OpenRouter, or point at a local Ollama/LM Studio), and
click **Test connection**. Keys are stored in the Windows Credential Manager —
never in plaintext.

## Where your data lives

User data is stored separately from the application so upgrades never touch it:

```
%LOCALAPPDATA%\TrendForge AI\
├── projects\   ├── exports\   ├── cache\
├── logs\       ├── backups\   ├── settings\   └── temp\
```
The application files live under your chosen install directory (e.g.
`C:\Program Files\TrendForge AI`).

## Portable version

Prefer no install? Download `TrendForge-AI-<version>-portable.zip`, extract it,
and run `TrendForge AI.exe` directly.

## Uninstall

Use **Settings → Apps** or the Start Menu uninstaller. You'll be asked whether
to keep or delete your user data (projects, database, settings, backups).

## System requirements

- Windows 10 or 11 (64-bit)
- Microsoft Edge WebView2 runtime (installed automatically if missing)
- ~300 MB disk space
