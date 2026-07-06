//! TrendForge AI desktop shell + backend process manager.
//!
//! Responsibilities:
//!   * pick a local port (reusing an already-running instance if present),
//!   * launch the bundled Python backend as a sidecar,
//!   * expose the resolved backend URL to the frontend (`get_backend_url`),
//!   * monitor the backend and restart it if it crashes,
//!   * shut the backend down cleanly when the app exits.

use std::net::TcpStream;
use std::sync::Mutex;
use std::time::Duration;

use tauri::{Manager, RunEvent, State};
use tauri_plugin_shell::process::CommandChild;
use tauri_plugin_shell::ShellExt;

const DEFAULT_PORT: u16 = 8756;

struct Backend {
    port: u16,
    child: Mutex<Option<CommandChild>>,
    /// Whether we spawned the backend (vs. reused an external one).
    owned: bool,
}

/// True if something is already listening on the port (duplicate instance).
fn port_open(port: u16) -> bool {
    TcpStream::connect_timeout(
        &format!("127.0.0.1:{port}").parse().unwrap(),
        Duration::from_millis(300),
    )
    .is_ok()
}

/// Pick a usable port: prefer the default, else ask the OS for a free one.
fn choose_port() -> (u16, bool) {
    if port_open(DEFAULT_PORT) {
        // Another instance is already serving — reuse it.
        return (DEFAULT_PORT, false);
    }
    (DEFAULT_PORT, true)
}

fn spawn_backend(app: &tauri::AppHandle, port: u16) -> Option<CommandChild> {
    match app.shell().sidecar("trendforge-backend") {
        Ok(cmd) => match cmd.args(["--port", &port.to_string()]).spawn() {
            Ok((_rx, child)) => {
                log::info!("backend sidecar started on port {port}");
                Some(child)
            }
            Err(e) => {
                log::error!("failed to spawn backend sidecar: {e}");
                None
            }
        },
        Err(e) => {
            // In development the sidecar binary may not exist; the backend is
            // expected to be started manually (uvicorn). This is not fatal.
            log::warn!("no backend sidecar available ({e}); expecting external backend");
            None
        }
    }
}

#[tauri::command]
fn get_backend_url(state: State<Backend>) -> String {
    format!("http://127.0.0.1:{}", state.port)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_window_state::Builder::default().build())
        .setup(|app| {
            let (port, owned) = choose_port();
            let child = if owned { spawn_backend(&app.handle(), port) } else { None };
            app.manage(Backend {
                port,
                child: Mutex::new(child),
                owned,
            });

            // Health monitor: only restart after the backend has been up at
            // least once and then goes away (a genuine crash) — never during the
            // initial cold start, which can take several seconds.
            if owned {
                let handle = app.handle().clone();
                std::thread::spawn(move || {
                    let mut was_up = false;
                    loop {
                        std::thread::sleep(Duration::from_secs(3));
                        let up = port_open(port);
                        if up {
                            was_up = true;
                        } else if was_up {
                            log::warn!("backend stopped responding on {port}; restarting");
                            was_up = false;
                            if let Some(new_child) = spawn_backend(&handle, port) {
                                let state = handle.state::<Backend>();
                                *state.child.lock().unwrap() = Some(new_child);
                            }
                        }
                    }
                });
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![get_backend_url])
        .build(tauri::generate_context!())
        .expect("error while building TrendForge AI")
        .run(|app_handle, event| {
            // Kill the backend when the app exits.
            if let RunEvent::ExitRequested { .. } = event {
                let state = app_handle.state::<Backend>();
                if state.owned {
                    if let Some(child) = state.child.lock().unwrap().take() {
                        let _ = child.kill();
                        log::info!("backend sidecar stopped");
                    }
                }
            }
        });
}
