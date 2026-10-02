/** Web app manifest (served at /manifest.webmanifest) - makes Codeingo installable as an app. */
export default function manifest() {
  return {
    name: "Codeingo - learn to code",
    short_name: "Codeingo",
    description: "Learn to code with bite-sized, gamified lessons.",
    id: "/",
    start_url: "/learn",
    scope: "/",
    display: "standalone",
    orientation: "any",
    background_color: "#ffffff",
    theme_color: "#1d6ff2",
    categories: ["education", "productivity"],
    icons: [
      { src: "/icons/icon-192.png", sizes: "192x192", type: "image/png", purpose: "any" },
      { src: "/icons/icon-512.png", sizes: "512x512", type: "image/png", purpose: "any" },
      { src: "/icons/maskable-192.png", sizes: "192x192", type: "image/png", purpose: "maskable" },
      { src: "/icons/maskable-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
    ],
    shortcuts: [
      { name: "Continue learning", url: "/learn", icons: [{ src: "/icons/icon-192.png", sizes: "192x192" }] },
      { name: "Practice", url: "/practice", icons: [{ src: "/icons/icon-192.png", sizes: "192x192" }] },
      { name: "Daily challenge", url: "/daily", icons: [{ src: "/icons/icon-192.png", sizes: "192x192" }] },
    ],
  };
}
