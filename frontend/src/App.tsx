import { useEffect } from "react";
import { RouterProvider } from "react-router-dom";
import { Toaster } from "sonner";
import { router } from "@/routes";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import { applyTheme, getTheme } from "@/lib/theme";

export default function App() {
  // Apply the persisted theme before anything renders visually.
  useEffect(() => {
    applyTheme(getTheme());
  }, []);

  return (
    <ErrorBoundary>
      <RouterProvider router={router} />
      <Toaster
        theme="dark"
        position="bottom-right"
        toastOptions={{
          style: {
            background: "var(--card)",
            border: "1px solid var(--border)",
            color: "var(--foreground)",
          },
        }}
      />
    </ErrorBoundary>
  );
}
