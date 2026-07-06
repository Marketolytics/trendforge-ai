/** Persisted UI state, restored on the next launch. */

interface AppState {
  lastRoute?: string;
  sidebarCollapsed?: boolean;
  lastTrendId?: number;
  onboardingDismissed?: boolean;
}

const KEY = "tf_app_state";

function read(): AppState {
  try {
    return JSON.parse(localStorage.getItem(KEY) || "{}") as AppState;
  } catch {
    return {};
  }
}

export function getAppState(): AppState {
  return read();
}

export function patchAppState(patch: Partial<AppState>): void {
  localStorage.setItem(KEY, JSON.stringify({ ...read(), ...patch }));
}
