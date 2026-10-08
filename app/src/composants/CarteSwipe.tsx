import { useEffect, useRef, useState } from 'react';
import type { Carte, Reponse } from '../types';

const SEUIL_X = 90;
const SEUIL_Y = 110;

interface Props {
  carte: Carte;
  important: boolean;
  onImportant: () => void;
  onReponse: (r: Reponse) => void;
}

const TYPES: Record<string, string> = {
  ensemble: 'Texte entier',
  partie: 'Partie du budget',
  article: 'Article de loi',
  amendement: 'Amendement',
  resolution: 'Résolution',
};

export function CarteSwipe({ carte, important, onImportant, onReponse }: Props) {
  const [delta, setDelta] = useState({ x: 0, y: 0 });
  const [sortie, setSortie] = useState<Reponse | null>(null);
  const depart = useRef<{ x: number; y: number } | null>(null);

  const repondre = (r: Reponse) => {
    if (sortie) return;
    setSortie(r);
    setTimeout(() => {
      onReponse(r);
      setSortie(null);
      setDelta({ x: 0, y: 0 });
    }, 220);
  };

  // Clavier : flèches pour voter, « é » ou « s » pour l'étoile
  useEffect(() => {
    const touche = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight') repondre('pour');
      else if (e.key === 'ArrowLeft') repondre('contre');
      else if (e.key === 'ArrowDown') { e.preventDefault(); repondre('passe'); }
      else if (e.key === 's' || e.key === 'é') onImportant();
    };
    window.addEventListener('keydown', touche);
    return () => window.removeEventListener('keydown', touche);
  });

  const onDown = (e: React.PointerEvent) => {
    if ((e.target as HTMLElement).closest('a,button')) return;
    depart.current = { x: e.clientX, y: e.clientY };
    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  };
  const onMove = (e: React.PointerEvent) => {
    if (!depart.current) return;
    setDelta({ x: e.clientX - depart.current.x, y: Math.max(0, e.clientY - depart.current.y) });
  };
  const onUp = () => {
    if (!depart.current) return;
    depart.current = null;
    if (delta.x > SEUIL_X) repondre('pour');
    else if (delta.x < -SEUIL_X) repondre('contre');
    else if (delta.y > SEUIL_Y) repondre('passe');
    else setDelta({ x: 0, y: 0 });
  };

  const indice: Reponse | null =
    delta.x > 40 ? 'pour' : delta.x < -40 ? 'contre' : delta.y > 60 ? 'passe' : null;

  const transform = sortie
    ? sortie === 'pour' ? 'translateX(130%) rotate(18deg)'
      : sortie === 'contre' ? 'translateX(-130%) rotate(-18deg)'
      : 'translateY(120%)'
    : `translate(${delta.x}px, ${delta.y}px) rotate(${delta.x / 18}deg)`;

  return (
    <div className="zone-carte">
      <article
        className={`carte ${indice ? 'indice-' + indice : ''}`}
        style={{ transform, transition: depart.current ? 'none' : 'transform .22s ease' }}
        onPointerDown={onDown}
        onPointerMove={onMove}
        onPointerUp={onUp}
        onPointerCancel={onUp}
        aria-live="polite"
      >
        <div className="tampon tampon-pour">POUR</div>
        <div className="tampon tampon-contre">CONTRE</div>
        <div className="tampon tampon-passe">JE NE SAIS PAS</div>

        <div className="carte-entete">
          <span className="puce-theme">{carte.theme}</span>
          <span className="type-vote">{TYPES[carte.type] ?? carte.type}</span>
        </div>
        <h2 className="carte-titre">{carte.titre}</h2>
        <p className="carte-resume">{carte.ce_que_ca_change}</p>
        <p className="carte-contexte">{carte.contexte}</p>
        <div className="carte-pied">
          <a href={carte.liens.texte ?? carte.liens.dossier} target="_blank" rel="noreferrer">
            Lire le texte officiel ↗
          </a>
          <button
            className={`etoile ${important ? 'active' : ''}`}
            onClick={onImportant}
            aria-pressed={important}
            title="Ce sujet compte beaucoup pour moi : la carte compte double"
          >
            {important ? '★' : '☆'} <span>Important pour moi</span>
          </button>
        </div>
      </article>

      <div className="boutons-vote">
        <button className="btn-vote contre" onClick={() => repondre('contre')} aria-label="Contre">
          <span>✕</span>Contre
        </button>
        <button className="btn-vote passe" onClick={() => repondre('passe')} aria-label="Je ne sais pas">
          <span>↓</span>Je ne sais pas
        </button>
        <button className="btn-vote pour" onClick={() => repondre('pour')} aria-label="Pour">
          <span>✓</span>Pour
        </button>
      </div>
    </div>
  );
}
