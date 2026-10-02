import Certificate from "@/views/Certificate";

export const metadata = { title: "Certificate" };

export default async function Page({ params }) {
  const { code } = await params;
  return <Certificate code={String(code).slice(0, 32)} />;
}
