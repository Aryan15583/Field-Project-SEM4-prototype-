/** Web app manifest (served at /manifest.webmanifest) - makes Codeingo installable as an app. */
const V = "?v=3"; // bump when the icon artwork changes: installed apps and browsers cache icons by URL

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
    background_color: "#faf8f3",
    theme_color: "#254ec4",
    categories: ["education", "productivity"],
    icons: [
      { src: `/icons/icon-192.png${V}`, sizes: "192x192", type: "image/png", purpose: "any" },
      { src: `/icons/icon-512.png${V}`, sizes: "512x512", type: "image/png", purpose: "any" },
      { src: `/icons/maskable-192.png${V}`, sizes: "192x192", type: "image/png", purpose: "maskable" },
      { src: `/icons/maskable-512.png${V}`, sizes: "512x512", type: "image/png", purpose: "maskable" },
    ],
    shortcuts: [
      { name: "Continue learning", url: "/learn", icons: [{ src: `/icons/icon-192.png${V}`, sizes: "192x192" }] },
      { name: "Practice", url: "/practice", icons: [{ src: `/icons/icon-192.png${V}`, sizes: "192x192" }] },
      { name: "Daily challenge", url: "/daily", icons: [{ src: `/icons/icon-192.png${V}`, sizes: "192x192" }] },
    ],
  };
}
