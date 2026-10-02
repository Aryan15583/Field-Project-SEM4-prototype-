import { RequireAuth } from "@/components/guards";
import Practice from "@/views/Practice";

export const metadata = { title: "Practice" };

export default async function Page({ searchParams }) {
  const sp = await searchParams;
  const course = typeof sp.course === "string" ? sp.course.slice(0, 40) : undefined;
  return (
    <RequireAuth>
      <Practice course={course} />
    </RequireAuth>
  );
}
