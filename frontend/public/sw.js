// Marffet Service Worker — v1.0 (minimal offline shell)
const CACHE_NAME = "marffet-v1";
const OFFLINE_URL = "/offline.html";

// Pre-cache essential shell on install
self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) =>
            cache.addAll([
                OFFLINE_URL,
                "/manifest.json",
            ])
        )
    );
    self.skipWaiting();
});

// Clean up old caches on activate
self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(
                keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
            )
        )
    );
    self.clients.claim();
});

// Network-first strategy: try network, fall back to cache/offline page
self.addEventListener("fetch", (event) => {
    // Skip non-GET requests, API calls, and Next.js internals
    if (
        event.request.method !== "GET" ||
        event.request.url.includes("/api/") ||
        event.request.url.includes("/auth/") ||
        event.request.url.includes("/_next/") ||
        event.request.url.includes("/hot-update")
    ) {
        return;
    }

    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // Cache successful page responses
                if (response.ok && response.type === "basic") {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                }
                return response;
            })
            .catch(() =>
                caches.match(event.request).then((cached) => cached || caches.match(OFFLINE_URL))
            )
    );
});
