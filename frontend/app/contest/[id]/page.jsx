import { RequireAuth } from "@/components/guards";
import Contest from "@/views/Contest";

export const metadata = { title: "Contest" };

export default async function Page({ params }) {
  const { id } = await params;
  return (
    <RequireAuth>
      <Contest id={String(Number.parseInt(id, 10) || 0)} />
    </RequireAuth>
  );
}
