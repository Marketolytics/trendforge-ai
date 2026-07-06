/** Desktop notifications with a local enable flag and permission handling. */

const KEY = "tf_notifications";

export function notificationsEnabled(): boolean {
  return localStorage.getItem(KEY) !== "false";
}

export function setNotificationsEnabled(enabled: boolean): void {
  localStorage.setItem(KEY, enabled ? "true" : "false");
  if (enabled) void requestNotificationPermission();
}

export async function requestNotificationPermission(): Promise<boolean> {
  if (!("Notification" in window)) return false;
  if (Notification.permission === "granted") return true;
  if (Notification.permission === "denied") return false;
  const result = await Notification.requestPermission();
  return result === "granted";
}

export function notify(title: string, body?: string): void {
  if (!notificationsEnabled()) return;
  if (!("Notification" in window) || Notification.permission !== "granted") return;
  try {
    new Notification(title, { body, silent: false });
  } catch {
    /* ignore */
  }
}
