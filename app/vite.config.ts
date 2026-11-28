import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

// BASE : chemin de publication (ex. « /depute-d-un-jour/ » sur GitHub Pages)
export default defineConfig({
  base: process.env.BASE ?? '/',
  // Version affichée dans le pied de page et le mail de signalement : date de construction
  define: { __VERSION__: JSON.stringify(new Date().toISOString().slice(0, 10)) },
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
        background_color: '#f4f5f8',
        display: 'standalone',
        icons: [
          { src: 'icone.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any maskable' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,json,woff2}'],
        runtimeCaching: [{ urlPattern: /\/data\/.*\.json$/, handler: 'StaleWhileRevalidate' }],
      },
    }),
  ],
});
