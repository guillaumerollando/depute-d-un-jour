import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

// BASE : chemin de publication (ex. « /depute-d-un-jour/ » sur GitHub Pages)
export default defineConfig({
  base: process.env.BASE ?? '/',
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['icone.svg'],
      manifest: {
        name: "Député d'un jour",
        short_name: "Député d'un jour",
        description: "Vote sur de vrais textes de l'Assemblée nationale et découvre de quels groupes tu es le plus proche, d'après leurs votes réels.",
        lang: 'fr',
        theme_color: '#1d2b4f',
        background_color: '#f6f4ef',
        display: 'standalone',
        icons: [
          { src: 'icone.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any maskable' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,json}'],
        runtimeCaching: [{ urlPattern: /\/data\/.*\.json$/, handler: 'StaleWhileRevalidate' }],
      },
    }),
  ],
});
