import { useMemo, useState } from 'react';
import type { Carte, Donnees, Vote } from '../types';
import { deputeJumeau, paliers, scores } from '../score';
import { Hemicycle } from './Hemicycle';

interface Props {
  donnees: Donnees;
  votes: Vote[];
  onContinuer: (() => void) | null;
  onRecommencer: () => void;
  onMethode: () => void;
}

const REPONSES = { pour: 'Pour', contre: 'Contre', passe: 'Je ne sais pas' } as const;

function listeNoms(noms: string[]) {
  return noms.length <= 1 ? noms.join('') : `${noms.slice(0, -1).join(', ')} et ${noms[noms.length - 1]}`;
}

export function Resultat({ donnees, votes, onContinuer, onRecommencer, onMethode }: Props) {
  const index = useMemo(() => new Map(donnees.cartes.map((c) => [c.uid, c])), [donnees]);
  const liste = useMemo(() => scores(donnees.groupes, index, votes), [donnees, index, votes]);
  const niveaux = useMemo(() => paliers(liste), [liste]);
  const jumeau = useMemo(() => deputeJumeau(donnees.deputes, index, votes), [donnees, index, votes]);
  const repondus = votes.filter((v) => v.reponse !== 'passe').length;
  const premiers = niveaux[0] ?? [];
  const derniers = niveaux.length > 1 ? niveaux[niveaux.length - 1] : [];
  const proches = new Set(premiers.map((s) => s.groupe.id));
  const [copie, setCopie] = useState(false);

  const partager = async () => {
    const texte =
      `Député d'un jour : sur ${repondus} votes réels de l'Assemblée, j'ai voté comme ` +
      `${listeNoms(premiers.map((s) => s.groupe.sigle))} dans ${premiers[0]?.pourcentage ?? 0} % des cas. Et toi ?`;
    try {
      if (navigator.share) await navigator.share({ title: "Député d'un jour", text: texte, url: location.href });
      else { await navigator.clipboard.writeText(`${texte} ${location.href}`); setCopie(true); }
    } catch { /* partage annulé */ }
  };

  if (repondus === 0)
    return (
      <section className="ecran resultat">
        <h1>Pas encore de résultat</h1>
        <p>Tu as passé toutes les cartes : réponds pour ou contre à quelques votes pour te comparer aux groupes.</p>
        <button className="btn-principal" onClick={onRecommencer}>Recommencer</button>
      </section>
    );

  return (
    <section className="ecran resultat">
      <p className="surtitre">Ton résultat · {repondus} vote{repondus > 1 ? 's' : ''}</p>
      <h1>
        Tu as voté comme {listeNoms(premiers.map((s) => s.groupe.nom))}
        <span className="pourcentage"> dans {premiers[0]?.pourcentage} % des cas</span>
      </h1>
      {premiers.length > 1 && (
        <p className="note">Ces groupes sont ex aequo : leurs scores diffèrent de moins de 10 points.</p>
      )}

      <Hemicycle groupes={donnees.groupes} proches={proches} />

      {derniers.length > 0 && (
        <p className="eloigne">
          Le plus éloigné : <strong>{listeNoms(derniers.map((s) => s.groupe.nom))}</strong>{' '}
          ({derniers[0].pourcentage} % d'accord)
        </p>
      )}

      <h2>Ton accord avec chaque groupe</h2>
      <ol className="classement">
        {liste.map((s) => (
          <li key={s.groupe.id}>
            <span className="pastille" style={{ background: s.groupe.couleur }} />
            <span className="nom-groupe">
              <strong>{s.groupe.sigle}</strong> <small>{s.groupe.nom}</small>
            </span>
            <span className="barre">
              <span style={{ width: `${s.pourcentage ?? 0}%`, background: s.groupe.couleur }} />
            </span>
            <span className="valeur">
              {s.pourcentage === null ? '—' : `${s.pourcentage} %`}
              <small>{s.cartes} carte{s.cartes > 1 ? 's' : ''}</small>
            </span>
          </li>
        ))}
      </ol>
      <p className="note">
        Pourcentage de cartes où ce groupe a voté comme toi, parmi celles où il avait une position claire.
        Les cartes marquées d'une étoile comptent double.
      </p>

      {jumeau && (
        <div className="encart jumeau">
          <p className="surtitre">Ton député jumeau</p>
          <p>
            <strong>{jumeau.depute.nom}</strong> ({donnees.groupes.find((g) => g.id === jumeau.depute.groupe)?.sigle ?? 'non inscrit'}
            {jumeau.depute.departement ? `, ${jumeau.depute.departement}` : ''}) a voté comme toi
            dans {jumeau.pourcentage} % des cas.
          </p>
        </div>
      )}

      <div className="actions">
        {onContinuer && <button className="btn-principal" onClick={onContinuer}>Affiner avec 10 votes de plus</button>}
        <button className="btn-secondaire" onClick={partager}>{copie ? 'Lien copié !' : 'Partager'}</button>
        <button className="btn-secondaire" onClick={onRecommencer}>Recommencer</button>
      </div>

      <h2>Vote par vote</h2>
      <p className="note">Compare ta réponse aux votes réels des groupes. Touche une carte pour voir ce qu'ils ont dit.</p>
      <ul className="detail-votes">
        {votes.map((v) => {
          const c = index.get(v.uid);
          return c ? <DetailVote key={v.uid} carte={c} vote={v} donnees={donnees} /> : null;
        })}
      </ul>

      <p className="avertissement">
        Ce résultat compare tes réponses à des votes réels. Ce n'est ni un sondage, ni une consigne de vote.{' '}
        <button className="lien" onClick={onMethode}>Comment c'est calculé ?</button>
      </p>
    </section>
  );
}

function DetailVote({ carte, vote, donnees }: { carte: Carte; vote: Vote; donnees: Donnees }) {
  const [ouvert, setOuvert] = useState(false);
  return (
    <li className={`detail-vote ${ouvert ? 'ouvert' : ''}`}>
      <button className="detail-tete" onClick={() => setOuvert(!ouvert)} aria-expanded={ouvert}>
        <span className={`ta-reponse ${vote.reponse}`}>{REPONSES[vote.reponse]}{vote.important ? ' ★' : ''}</span>
        <span className="detail-titre">{carte.titre}</span>
        <span className="chevron">{ouvert ? '−' : '+'}</span>
      </button>
      <div className="positions">
        {donnees.groupes.map((g) => {
          const p = carte.positions[g.id];
          const neutre = carte.neutralises.includes(g.id);
          const accord = p && vote.reponse !== 'passe' && p === vote.reponse;
          return (
            <span
              key={g.id}
              className={`position ${p ?? 'aucune'} ${accord ? 'accord' : ''}`}
              style={{ borderColor: g.couleur }}
              title={`${g.nom} : ${p ?? (neutre ? 'position non comptée (vote ambigu)' : 'pas de position claire')}`}
            >
              {g.sigle} {p === 'pour' ? '✓' : p === 'contre' ? '✕' : '·'}
            </span>
          );
        })}
      </div>
      {ouvert && (
        <div className="detail-corps">
          {carte.aujourdhui && <p className="aujourdhui"><strong>Aujourd'hui</strong> {carte.aujourdhui}</p>}
          <p>{carte.ce_que_ca_change}</p>
          {carte.arguments && (
            <div className="arguments-corps">
              <p className="argument pour"><span>Pour</span>{carte.arguments.pour}</p>
              <p className="argument contre"><span>Contre</span>{carte.arguments.contre}</p>
            </div>
          )}
          <p className="carte-contexte">
            {carte.contexte} Résultat à l'Assemblée : <strong>{carte.resultat === 'adopté' ? 'adopté' : 'rejeté'}</strong>.
          </p>
          {carte.neutralises.length > 0 && (
            <p className="note">
              Non comptés sur cette carte : {carte.neutralises.map((id) => donnees.groupes.find((g) => g.id === id)?.sigle).join(', ')}.
              Ces groupes ont déclaré soutenir l'objectif, ou s'y opposer, tout en votant dans l'autre sens pour une autre raison.
            </p>
          )}
          {Object.keys(carte.citations).length > 0 && (
            <div className="citations">
              <p className="surtitre">Ce qu'ils ont dit dans l'hémicycle</p>
              {donnees.groupes.filter((g) => carte.citations[g.id]).map((g) => (
                <blockquote key={g.id} style={{ borderColor: g.couleur }}>
                  « {carte.citations[g.id].citation} »
                  <cite>{carte.citations[g.id].orateur} ({g.sigle})</cite>
                </blockquote>
              ))}
            </div>
          )}
          <p className="liens">
            <a href={carte.liens.scrutin} target="_blank" rel="noreferrer">Le scrutin</a>
            <a href={carte.liens.dossier} target="_blank" rel="noreferrer">Le dossier</a>
            {carte.liens.texte && <a href={carte.liens.texte} target="_blank" rel="noreferrer">Le texte</a>}
            {carte.liens.compte_rendu && <a href={carte.liens.compte_rendu} target="_blank" rel="noreferrer">Le débat</a>}
          </p>
        </div>
      )}
    </li>
  );
}
