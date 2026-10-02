import { Nunito } from "next/font/google";
import { headers } from "next/headers";
import Providers from "./providers";
import "./globals.css";

export const metadata = {
  title: { default: "Codeingo", template: "%s · Codeingo" },
  description: "Codeingo - learn to code with bite-sized, gamified lessons.",
  icons: { icon: "/favicon.svg", apple: "/icons/apple-touch-icon.png" },
  appleWebApp: { capable: true, title: "Codeingo", statusBarStyle: "default" },
  referrer: "strict-origin-when-cross-origin",
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#000000" },
  ],
};

// Rounded, friendly type (self-hosted by Next at build time - no runtime request to Google).
const nunito = Nunito({ subsets: ["latin"], weight: ["600", "700", "800", "900"], display: "swap", variable: "--font-nunito" });

// Applies the saved/system theme before first paint (no light->dark flash).
const THEME_BOOTSTRAP = `(function(){var t=null;try{t=localStorage.getItem("cg_theme")}catch(e){}
var d=t==="dark"||((!t||t==="system")&&matchMedia("(prefers-color-scheme: dark)").matches);
document.documentElement.classList.toggle("dark",d)})();`;

export default async function RootLayout({ children }) {
  // Reading the request makes every page dynamically rendered, which the per-request CSP nonce requires.
  const nonce = (await headers()).get("x-nonce") ?? undefined;
  return (
    <html lang="en" className={nunito.variable} data-scroll-behavior="smooth" suppressHydrationWarning>
      <head>
        <script nonce={nonce} dangerouslySetInnerHTML={{ __html: THEME_BOOTSTRAP }} />
      </head>
      <body className="bg-bg text-ink">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
