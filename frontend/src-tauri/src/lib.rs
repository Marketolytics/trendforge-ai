//! TrendForge AI desktop shell.
//!
//! The window loads the React frontend, which talks to the local FastAPI
//! backend over HTTP. Native commands can be added here as the app grows.

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .run(tauri::generate_context!())
        .expect("error while running TrendForge AI");
}
