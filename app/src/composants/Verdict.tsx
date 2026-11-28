import type { Carte, Reponse } from '../types';

/** Après chaque vote : ce qu'a décidé l'Assemblée, avec le décompte officiel. Jamais la position des groupes
 *  (révélée seulement à la fin, pour ne pas influencer les votes suivants). */
export function Verdict({ carte, reponse }: { carte: Carte; reponse: Reponse }) {
  const adopte = carte.resultat === 'adopté';
  const d = carte.decompte;
  const ecart = d ? Math.abs(d.pour - d.contre) : null;
  const comme = reponse === 'passe' ? null : (adopte ? 'pour' : 'contre') === reponse;
  return (
    <div className={`verdict ${adopte ? 'adopte' : 'rejete'}`} role="status">
      <p className="verdict-titre">{carte.titre}</p>
      <p className="verdict-ligne">
        <strong>{adopte ? 'Adopté' : 'Rejeté'}</strong>
        {d && <span className="verdict-voix"> · {d.pour} pour, {d.contre} contre{ecart !== null && ecart <= 10 ? ` · à ${ecart} voix près` : ''}</span>}
        {comme !== null && <span className="verdict-toi">{comme ? 'Comme toi' : 'Pas comme toi'}</span>}
      </p>
    </div>
  );
}
