/* Codeingo service worker: offline page + caching of immutable assets. Never caches the API
 * (progress, answers and sessions always go to the server) or signed-in pages. */
const VERSION = "v3";
const STATIC = `codeingo-static-${VERSION}`;
const PRECACHE = ["/offline.html", "/favicon.svg", "/icons/icon-192.png"];
// content-hashed or versioned files that never change at the same URL (not /icons/: same names, new artwork)
const IMMUTABLE = [/^\/_next\/static\//, /^\/pyodide\//, /^\/sqljs\//, /^\/typescript\//];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(STATIC).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith("codeingo-") && k !== STATIC).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin || url.pathname.startsWith("/api/")) return;

  if (req.mode === "navigate") {
    // pages: always the network (they carry a fresh CSP nonce); the offline page when there is none
    event.respondWith(fetch(req).catch(() => caches.match("/offline.html")));
    return;
  }
  if (IMMUTABLE.some((re) => re.test(url.pathname)) && !req.headers.has("range")) {
    event.respondWith(
      caches.open(STATIC).then(async (cache) => {
        const hit = await cache.match(req);
        if (hit) return hit;
        const res = await fetch(req);
        if (res.ok && res.type === "basic") cache.put(req, res.clone());
        return res;
      }),
    );
  }
});
