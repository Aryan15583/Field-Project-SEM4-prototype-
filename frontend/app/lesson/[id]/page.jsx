import { RequireAuth } from "@/components/guards";
import Lesson from "@/views/Lesson";

export const metadata = { title: "Lesson" };

export default async function Page({ params }) {
  const { id } = await params;
  return (
    <RequireAuth>
      <Lesson id={id} />
    </RequireAuth>
  );
}
