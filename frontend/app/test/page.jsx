import { RequireAuth } from "@/components/guards";
import Test from "@/views/Test";

export const metadata = { title: "Test" };

const one = (v) => (typeof v === "string" ? v.slice(0, 40) : undefined);

export default async function Page({ searchParams }) {
  const sp = await searchParams;
  return (
    <RequireAuth>
      <Test course={one(sp.course)} unitId={one(sp.unit)} section={one(sp.section)} />
    </RequireAuth>
  );
}
