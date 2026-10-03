import Link from "next/link";
import { Mascot } from "@/components/ui";

/** The 404 screen - also shown for pages a signed-in user isn't allowed to know about (e.g. /admin). */
export default function NotFoundView() {
  return (
    <div className="grid min-h-screen place-items-center text-center">
      <div>
        <Mascot size={110} mood="sad" className="mx-auto" />
        <h1 className="mt-4 text-2xl font-black">404 - page not found</h1>
        <Link href="/learn" className="btn-link">
          Back to learning
        </Link>
      </div>
    </div>
  );
}
