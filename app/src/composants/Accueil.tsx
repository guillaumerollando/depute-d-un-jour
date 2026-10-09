import type { Donnees, Vote } from '../types';

interface Props {
  donnees: Donnees;
  reprise: { ecran: string; votes: Vote[]; objectif: number } | null;
  onReprendre: () => void;
  onCommencer: () => void;
  onMethode: () => void;
}

const date = (iso: string) =>
  new Date(iso).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });

// Écran tactile : on touche les boutons ; à la souris, on peut aussi glisser la carte
const tactile = typeof window !== 'undefined' && window.matchMedia?.('(pointer: coarse)').matches;

export function Accueil({ donnees, reprise, onReprendre, onCommencer, onMethode }: Props) {
  return (
    <section className="ecran accueil">
      <div className="logo" aria-hidden="true">
        <svg viewBox="0 0 64 36"><path d="M4 34a28 28 0 0 1 56 0" /><path d="M14 34a18 18 0 0 1 36 0" /><path d="M24 34a8 8 0 0 1 16 0" /></svg>
      </div>
      <h1>Député d'un jour</h1>
      <p className="accroche">
        Vote sur de vrais textes de l'Assemblée nationale. Découvre de quels groupes tu es le plus proche,
        <strong> d'après ce qu'ils ont réellement voté</strong>, pas d'après ce qu'ils promettent.
      </p>

      <ol className="regles">
        {tactile ? (
          <>
            <li><span className="geste pour">✓</span> <span>Touche <strong>Pour</strong> si tu votes pour</span></li>
            <li><span className="geste contre">✕</span> <span>Touche <strong>Contre</strong> si tu votes contre</span></li>
          </>
        ) : (
          <>
            <li><span className="geste pour">→</span> <span>Glisse la carte à droite ou clique <strong>Pour</strong></span></li>
            <li><span className="geste contre">←</span> <span>Glisse la carte à gauche ou clique <strong>Contre</strong></span></li>
          </>
        )}
        <li><span className="geste passe">?</span> <span>Touche « Je ne sais pas » si <strong>tu n'as pas d'avis</strong></span></li>
        <li><span className="geste g-etoile">★</span> <span>Touche l'étoile si le sujet <strong>compte beaucoup</strong> pour toi</span></li>
        <li><span className="geste g-arguments">⚖</span> <span>Pas sûr ? Lis <strong>les arguments</strong> des deux camps</span></li>
      </ol>

      {reprise ? (
        <div className="reprise">
          <button className="btn-principal grand" onClick={onReprendre}>
            {reprise.ecran === 'jeu'
              ? `Reprendre mes votes · ${reprise.votes.length}/${reprise.objectif}`
              : 'Revoir mon dernier résultat'}
          </button>
          <button className="btn-secondaire grand" onClick={onCommencer}>Recommencer · 15 votes</button>
        </div>
      ) : (
        <button className="btn-principal grand" onClick={onCommencer}>Commencer · 15 votes</button>
      )}

      <p className="garanties">
        Aucun compte, aucune donnée collectée : tout se passe sur ton téléphone.
        Cartes sélectionnées par une méthode publique, sans choix éditorial.
      </p>
      <button className="lien" onClick={onMethode}>Comment ça marche ?</button>
      <p className="source">
        {donnees.meta.cartes} votes tirés de {donnees.meta.scrutins_analyses.toLocaleString('fr-FR')} scrutins publics
        · données de l'Assemblée nationale au {date(donnees.meta.date_donnees)}
      </p>
    </section>
  );
}
