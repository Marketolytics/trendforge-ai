import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}
interface State {
  error: Error | null;
}

/** Catches render errors so the whole app never crashes to a blank screen. */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("Unhandled UI error:", error, info.componentStack);
  }

  render(): ReactNode {
    if (this.state.error) {
      return (
        <div className="flex h-screen w-screen flex-col items-center justify-center gap-4 bg-[var(--background)] p-6 text-center text-[var(--foreground)]">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--danger)]/15 text-[var(--danger)] text-2xl">
            !
          </div>
          <h1 className="text-lg font-semibold">Something went wrong</h1>
          <p className="max-w-md text-sm text-[var(--muted-foreground)]">
            The interface hit an unexpected error. Your data is safe — reloading usually fixes it.
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => this.setState({ error: null })}
              className="rounded-md border border-[var(--border)] px-4 py-2 text-sm hover:bg-[var(--muted)]"
            >
              Try again
            </button>
            <button
              onClick={() => window.location.reload()}
              className="rounded-md bg-[var(--accent)] px-4 py-2 text-sm text-[var(--accent-foreground)]"
            >
              Reload app
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
