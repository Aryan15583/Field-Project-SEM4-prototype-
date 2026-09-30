import AppShell from "@/components/AppShell";
import { RequireAuth } from "@/components/guards";

export default function AppLayout({ children }) {
  return (
    <RequireAuth>
      <AppShell>{children}</AppShell>
    </RequireAuth>
  );
}
