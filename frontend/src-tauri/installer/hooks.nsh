; NSIS installer hooks for TrendForge AI.
; Wired via tauri.conf.json -> bundle.windows.nsis.installerHooks.

; On uninstall, offer a clean removal of user data (projects, database,
; settings, backups). User data lives OUTSIDE Program Files so a normal
; uninstall/upgrade never touches it — this prompt is opt-in.
!macro NSIS_HOOK_PREUNINSTALL
  MessageBox MB_YESNO|MB_ICONEXCLAMATION \
    "Do you also want to delete your TrendForge AI user data?$\n$\n\
This permanently removes ALL projects, the database, settings and backups in:$\n\
$LOCALAPPDATA\TrendForge AI$\n$\n\
Choose No to keep your data for a future reinstall." \
    /SD IDNO IDNO tf_keep_data
  RMDir /r "$LOCALAPPDATA\TrendForge AI"
  tf_keep_data:
!macroend
