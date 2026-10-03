import { RequireAuth } from "@/components/guards";
import Admin from "@/views/Admin";

// a neutral title, so the browser tab doesn't reveal the page to someone who opens /admin by guessing
export const metadata = { title: { absolute: "Codeingo" } };

export default function Page() {
  return (
    <RequireAuth admin>
      <Admin />
    </RequireAuth>
  );
}
