/**
 * vibecoded: Vite build for pwnamap.
 *
 * Output: /dist/ at repo root — mounted as app/static/dist/ by the
 * multi-stage Dockerfile. Runtime requests NO external resources
 * except user-configurable map tiles (OSM default).
 */
import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';
import { viteStaticCopy } from 'vite-plugin-static-copy';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  root: __dirname,
  base: '/static/dist/',
  publicDir: false,
  build: {
    outDir: resolve(__dirname, '..', '..', 'dist'),
    emptyOutDir: true,
    sourcemap: false,
    minify: 'esbuild',
    cssCodeSplit: false,
    target: 'es2020',
    manifest: true,
    rollupOptions: {
      input: {
        dashboard:   resolve(__dirname, 'src/js/dashboard.js'),
        map:         resolve(__dirname, 'src/js/map.js'),
        pwnamap:     resolve(__dirname, 'src/js/pwnamap.js'),
        explore:     resolve(__dirname, 'src/js/explore.js'),
        handshakes:  resolve(__dirname, 'src/js/handshakes.js'),
        stats:       resolve(__dirname, 'src/js/stats.js'),
        settings:    resolve(__dirname, 'src/js/settings.js'),
        tools:       resolve(__dirname, 'src/js/tools.js'),
        login:       resolve(__dirname, 'src/js/login.js'),
        setup:       resolve(__dirname, 'src/js/setup.js'),
      },
      output: {
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]',
      },
    },
  },
  server: {
    port: 5173,
    proxy: { '/api': 'http://localhost:1337' },
  },
  plugins: [
    viteStaticCopy({
      targets: [
        { src: 'node_modules/leaflet.markercluster/dist/images/*', dest: 'images' },
        { src: 'node_modules/leaflet/dist/images/*', dest: 'images' },
      ],
    }),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg'],
      manifest: {
        name: 'pwnamap',
        short_name: 'pwnamap',
        description: 'Self-hosted companion for your pwnagotchi',
        theme_color: '#6200ea',
        background_color: '#121212',
        display: 'standalone',
        orientation: 'portrait-primary',
        start_url: '/',
        scope: '/',
        icons: [{ src: '/static/images/favicon.ico',
                  sizes: '64x64 32x32 24x24 16x16', type: 'image/x-icon' }],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,ico,woff2}'],
        navigateFallback: '/static/dist/dashboard.html',
        runtimeCaching: [
          { urlPattern: /^https:\/\/[abc]\.tile\.openstreetmap\.org\/.*/,
            handler: 'CacheFirst', options: { cacheName: 'osm-tiles',
              expiration: { maxEntries: 1000, maxAgeSeconds: 60*60*24*7 },
              cacheableResponse: { statuses: [0, 200] } } },
          { urlPattern: /^\/static\/.*/, handler: 'CacheFirst',
            options: { cacheName: 'pwnamap-static',
              expiration: { maxEntries: 100, maxAgeSeconds: 60*60*24*30 } } },
        ],
      },
    }),
  ],
});
