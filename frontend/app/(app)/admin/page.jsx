import { RequireAuth } from "@/components/guards";
import Admin from "@/views/Admin";

export const metadata = { title: "Admin" };

export default function Page() {
  return (
    <RequireAuth admin>
      <Admin />
    </RequireAuth>
  );
}
