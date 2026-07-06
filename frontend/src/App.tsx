import { RouterProvider } from "react-router-dom";
import { Toaster } from "sonner";
import { router } from "@/routes";

export default function App() {
  return (
    <>
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
    </>
  );
}
