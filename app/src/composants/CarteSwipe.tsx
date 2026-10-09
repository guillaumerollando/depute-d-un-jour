import { useEffect, useRef, useState } from 'react';
import type { Carte, Reponse } from '../types';

const SEUIL_X = 90;

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
  const [arguments_, setArguments] = useState(false);
  const [complet, setComplet] = useState(false);
  const [sortie, setSortie] = useState<Reponse | null>(null);
  const depart = useRef<{ x: number; y: number } | null>(null);
  const defilement = useRef<HTMLDivElement>(null);
  const zoneArguments = useRef<HTMLDivElement>(null);

  const basculerArguments = () => {
    const ouvrir = !arguments_;
    setArguments(ouvrir);
    if (ouvrir) setTimeout(() => zoneArguments.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50);
    else defilement.current?.scrollTo({ top: 0, behavior: 'smooth' });
  };

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
    // Sur écran tactile, le doigt sert à faire défiler la carte : le glissement n'est actif qu'à la souris
    if (e.pointerType !== 'mouse') return;
    if ((e.target as HTMLElement).closest('a,button')) return;
    depart.current = { x: e.clientX, y: e.clientY };
    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  };
  const onMove = (e: React.PointerEvent) => {
    if (!depart.current) return;
    // Seul le geste horizontal est suivi : le vertical sert à faire défiler le contenu de la carte
    setDelta({ x: e.clientX - depart.current.x, y: 0 });
  };
  const onUp = () => {
    if (!depart.current) return;
    depart.current = null;
    if (delta.x > SEUIL_X) repondre('pour');
    else if (delta.x < -SEUIL_X) repondre('contre');
    else setDelta({ x: 0, y: 0 });
  };
  // Le navigateur a pris la main pour faire défiler : on annule le glissement en cours
  const onCancel = () => { depart.current = null; setDelta({ x: 0, y: 0 }); };

  const indice: Reponse | null = delta.x > 40 ? 'pour' : delta.x < -40 ? 'contre' : null;

  const transform = sortie
    ? sortie === 'pour' ? 'translateX(130%) rotate(18deg)'
      : sortie === 'contre' ? 'translateX(-130%) rotate(-18deg)'
      : 'translateY(40px) scale(.96)'
    : `translateX(${delta.x}px) rotate(${delta.x / 18}deg)`;

  return (
    <div className="zone-carte">
      <article
        className={`carte entree ${indice ? 'indice-' + indice : ''}`}
        style={{ transform, transition: depart.current ? 'none' : 'transform .22s ease' }}
        onPointerDown={onDown}
        onPointerMove={onMove}
        onPointerUp={onUp}
        onPointerCancel={onCancel}
        aria-live="polite"
      >
        <div className="tampon tampon-pour">POUR</div>
        <div className="tampon tampon-contre">CONTRE</div>

        <div className="carte-defilement" ref={defilement}>
          <div className="carte-entete">
            <span className="puce-theme">{carte.theme}</span>
            <span className="type-vote">{TYPES[carte.type] ?? carte.type}</span>
          </div>
          <h2 className="carte-titre">{carte.titre}</h2>
          {carte.aujourdhui && (
            <p className="aujourdhui"><strong>Aujourd'hui</strong> {carte.aujourdhui}</p>
          )}
          <p className="carte-resume">
            {complet || !carte.resume_court ? carte.ce_que_ca_change : carte.resume_court}
            {carte.resume_court && (
              <button className="lien en-savoir" onClick={() => setComplet(!complet)}>
                {complet ? 'Moins' : 'En savoir plus'}
              </button>
            )}
          </p>
          <p className="carte-contexte">{carte.contexte}</p>
          <a className="lien-texte" href={carte.liens.texte ?? carte.liens.dossier} target="_blank" rel="noreferrer">
            Lire le texte officiel ↗
          </a>

          {carte.arguments && arguments_ && (
            <div className="arguments-corps" ref={zoneArguments}>
              <div className="argument pour">
                <span>Pour</span>{carte.arguments.pour}
                <blockquote className="bulle">« {carte.arguments.citation_pour} »<cite>Un député ayant voté pour</cite></blockquote>
              </div>
              <div className="argument contre">
                <span>Contre</span>{carte.arguments.contre}
                <blockquote className="bulle">« {carte.arguments.citation_contre} »<cite>Un député ayant voté contre</cite></blockquote>
              </div>
              <p className="note">Paroles réellement prononcées dans l'hémicycle. Les groupes sont révélés à la fin, pour ne pas influencer ton vote.</p>
            </div>
          )}
          {!carte.arguments && (
            <p className="note sans-arguments">Pour ce vote, l'un des deux camps ne s'est pas exprimé sur le fond pendant le débat : pas d'arguments à afficher.</p>
          )}
        </div>
      </article>

      <div className="barre-bas">
        <div className="actions-carte">
          {carte.arguments && (
            <button className={`btn-arguments ${arguments_ ? 'actif' : ''}`} onClick={basculerArguments} aria-expanded={arguments_}>
              ⚖ {arguments_ ? 'Masquer les arguments' : 'Pas sûr ? Les arguments'}
            </button>
          )}
          <button
            className={`etoile ${important ? 'active' : ''}`}
            onClick={onImportant}
            aria-pressed={important}
            title="Ce sujet compte beaucoup pour moi : la carte compte double"
          >
            {important ? '★' : '☆'} Important
          </button>
        </div>
      <div className="boutons-vote">
        <button className="btn-vote contre" onClick={() => repondre('contre')} aria-label="Contre">
          <span>✕</span>Contre
        </button>
        <button className="btn-vote passe" onClick={() => repondre('passe')} aria-label="Je ne sais pas">
          <span>?</span>Je ne sais pas
        </button>
        <button className="btn-vote pour" onClick={() => repondre('pour')} aria-label="Pour">
          <span>✓</span>Pour
        </button>
      </div>
      </div>
    </div>
  );
}
