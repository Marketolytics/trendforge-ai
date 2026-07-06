# PyInstaller spec — builds the backend into a single portable executable
# used as the Tauri sidecar (`trendforge-backend`).
#
# Build:  pyinstaller trendforge-backend.spec --noconfirm
# Output: dist/trendforge-backend(.exe)

from PyInstaller.utils.hooks import collect_all, collect_submodules

datas = [("app/services/ai/prompt_library", "app/services/ai/prompt_library")]
binaries = []
hiddenimports = []

# Bundle the full dependency trees that PyInstaller can't always trace.
for pkg in ("uvicorn", "google.genai", "keyring", "feedparser", "sqlmodel", "sqlalchemy"):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

hiddenimports += collect_submodules("uvicorn")
hiddenimports += [
    "app.main",
    "keyring.backends.Windows",
    "win32ctypes.core",
]

a = Analysis(
    ["run_server.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="trendforge-backend",
    console=True,          # keep stderr for the launcher's logs
    onefile=True,
    upx=False,
)
