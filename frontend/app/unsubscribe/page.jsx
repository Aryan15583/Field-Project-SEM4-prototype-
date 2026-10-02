import Unsubscribe from "@/views/Unsubscribe";

export const metadata = { title: "Email preferences" };

export default async function Page({ searchParams }) {
  const { u = "", t = "" } = await searchParams;
  return <Unsubscribe u={String(u).slice(0, 12)} t={String(t).slice(0, 64)} />;
}
