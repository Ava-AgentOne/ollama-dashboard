const CACHE_NAME = 'ollama-dashboard-v0.9';
const SHELL_ASSETS = [
  '/',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/apple-touch-icon.png',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(SHELL_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Never cache API calls — always go to network
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/proxy/')) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then(cached => {
      // Network first, fall back to cache for app shell
      return fetch(event.request)
        .then(response => {
          // Cache successful responses
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() => cached || new Response('Offline', { status: 503 }));
    })
  );
});
