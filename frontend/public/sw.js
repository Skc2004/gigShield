// Simple Service worker for PWA installation capability
self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  // Clear caches if any
});

self.addEventListener('fetch', (e) => {
  // Network first for demo purposes
});
