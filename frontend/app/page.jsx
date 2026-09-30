import { Suspense } from "react";
import { PublicOnly } from "@/components/guards";
import Landing from "@/views/Landing";

export default function Page() {
  return (
    <PublicOnly>
      <Suspense>
        <Landing />
      </Suspense>
    </PublicOnly>
  );
}
