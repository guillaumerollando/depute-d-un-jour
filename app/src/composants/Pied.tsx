import { useState } from 'react';
import type { Donnees } from '../types';
import { partagerSite } from '../partage';

const MAIL = 'rollandostudio@gmail.com';

// Lien mail prérempli : seulement ce qui aide à reproduire un problème, aucune donnée personnelle
function lienSignalement(ecran: string, donnees: Donnees) {
  const corps = [
    "Décris ce qui s'est passé :", '', '', '',
    '———',
    `Version : ${__VERSION__}`,
    `Données au : ${donnees.meta.date_donnees}`,
    `Écran : ${ecran}`,
    `Navigateur : ${navigator.userAgent}`,
    `Langue : ${navigator.language}`,
  ].join('\n');
  return `mailto:${MAIL}?subject=${encodeURIComponent("[Bug] Député d'un jour")}&body=${encodeURIComponent(corps)}`;
}

export function Pied({ ecran, donnees }: { ecran: string; donnees: Donnees }) {
  const [copie, setCopie] = useState(false);
  return (
    <footer className="pied">
      <button className="lien" onClick={async () => setCopie(await partagerSite())}>
        {copie ? 'Lien copié !' : 'Partager le site'}
      </button>
      <p className="pied-signaler">
        <a href={lienSignalement(ecran, donnees)}>Signaler un problème</a>
        <span> · on lit tout et on répond · {MAIL}</span>
      </p>
      <p className="pied-version">Député d'un jour · version {__VERSION__}</p>
      <a className="pied-studio" href="https://rollandostudio.com" target="_blank" rel="noopener">
        <svg viewBox="-8.23 -69.62 98.59 73.62" aria-hidden="true">
          <g transform="rotate(-10 6.39 0)"><path d="M6.39 -0.0 C6.39 -20.39 6.39 -40.78 6.39 -61.17 C15.04 -61.17 23.69 -61.17 32.34 -61.17 C35.74 -61.17 38.82 -60.91 41.57 -60.38 C44.32 -59.85 46.76 -59.08 48.89 -58.06 C51.02 -57.04 52.83 -55.81 54.31 -54.36 C55.79 -52.9 56.90 -51.24 57.65 -49.35 C58.39 -47.47 58.76 -45.38 58.76 -43.1 C58.76 -40.93 58.42 -38.99 57.74 -37.26 C57.06 -35.53 56.02 -34.01 54.63 -32.72 C53.24 -31.42 51.51 -30.37 49.44 -29.56 C47.37 -28.76 44.95 -28.17 42.17 -27.8 C42.17 -27.34 42.17 -26.88 42.17 -26.41 C45.63 -26.1 48.33 -25.33 50.28 -24.1 C52.22 -22.86 53.74 -21.25 54.82 -19.28 C55.90 -17.3 56.81 -14.92 57.55 -12.14 C58.73 -8.09 59.90 -4.05 61.08 -0.0 C55.55 -0.0 50.02 -0.0 44.49 -0.0 C43.59 -3.74 42.69 -7.48 41.80 -11.21 C41.30 -13.69 40.58 -15.6 39.62 -16.96 C38.66 -18.32 37.44 -19.26 35.96 -19.79 C34.48 -20.31 32.62 -20.57 30.40 -20.57 C27.37 -20.57 24.34 -20.57 21.32 -20.57 C21.32 -13.72 21.32 -6.86 21.32 -0.0 C16.34 -0.0 11.37 -0.0 6.39 -0.0 Z M21.32 -31.7 C24.65 -31.7 27.99 -31.7 31.33 -31.7 C35.09 -31.7 38.01 -32.42 40.08 -33.87 C42.15 -35.33 43.19 -37.63 43.19 -40.78 C43.19 -43.87 42.25 -46.15 40.36 -47.64 C38.48 -49.12 35.59 -49.86 31.70 -49.86 C28.24 -49.86 24.78 -49.86 21.32 -49.86 C21.32 -43.81 21.32 -37.75 21.32 -31.7 Z" /></g>
          <circle cx="73.36" cy="-13" r="13" />
        </svg>
        Fait par Rollando Studio
      </a>
    </footer>
  );
}
