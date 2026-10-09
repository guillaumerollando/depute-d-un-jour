import { useEffect, useMemo, useState } from 'react';
import type { Carte, Donnees, Reponse, Vote } from './types';
import { carteSuivante } from './score';
import { Accueil } from './composants/Accueil';
import { CarteSwipe } from './composants/CarteSwipe';
import { Resultat } from './composants/Resultat';
import { Methode } from './composants/Methode';

type Ecran = 'accueil' | 'jeu' | 'resultat' | 'methode';
const SERIE = 15; // nombre de votes proposés au départ
const RALLONGE = 10;

// Sauvegarde des votes en cours sur l'appareil : quitter la page (lien externe, rechargement) ne fait rien perdre
const CLE = 'depute-d-un-jour:partie';
interface Sauvegarde { ecran: Ecran; votes: Vote[]; objectif: number; carte: string | null; date?: number }
const DUREE_REPRISE = 7 * 24 * 60 * 60 * 1000; // des votes en cours restent proposés à la reprise pendant 7 jours

function lireSauvegarde(): Sauvegarde | null {
  try { return JSON.parse(localStorage.getItem(CLE) ?? 'null'); } catch { return null; }
}
function ecrireSauvegarde(s: Sauvegarde) {
  try { localStorage.setItem(CLE, JSON.stringify(s)); } catch { /* stockage indisponible : tant pis */ }
}

// Cartes vues lors des sessions précédentes (pour proposer autre chose la fois suivante)
const CLE_VUES = 'depute-d-un-jour:vues';
function lireVues(): Set<string> {
  try { return new Set(JSON.parse(localStorage.getItem(CLE_VUES) ?? '[]')); } catch { return new Set(); }
}
function memoriserVue(uid: string) {
  try {
    const v = lireVues();
    v.add(uid);
    localStorage.setItem(CLE_VUES, JSON.stringify([...v]));
  } catch { /* stockage indisponible */ }
}

/** « 1er février 2026 », « 28 octobre 2025 » */
function dateVote(iso: string) {
  const d = new Date(iso);
  const texte = d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
  return d.getDate() === 1 ? texte.replace(/^1 /, '1er ') : texte;
}

async function charger(): Promise<Donnees> {
  const base = import.meta.env.BASE_URL;
  const [groupes, cartes, deputes, meta] = await Promise.all(
    ['groupes', 'cartes', 'deputes', 'meta'].map((n) => fetch(`${base}data/${n}.json`).then((r) => r.json())),
  );
  return { groupes, cartes, deputes, meta };
}

export default function App() {
  const [donnees, setDonnees] = useState<Donnees | null>(null);
  const [erreur, setErreur] = useState(false);
  const [ecran, setEcran] = useState<Ecran>('accueil');
  const [retour, setRetour] = useState<Ecran>('accueil');
  const [votes, setVotes] = useState<Vote[]>([]);
  const [objectif, setObjectif] = useState(SERIE);
  const [carte, setCarte] = useState<Carte | null>(null);
  const [important, setImportant] = useState(false);

  const [reprise, setReprise] = useState<Sauvegarde | null>(null);

  useEffect(() => {
    charger()
      .then((d) => {
        // On ne reprend jamais tout seul : l'accueil propose de reprendre, et recommencer reste un choix
        const s = lireSauvegarde();
        const connues = new Set(d.cartes.map((c) => c.uid));
        const recente = s?.date && Date.now() - s.date < DUREE_REPRISE;
        if (s && recente && s.votes.length > 0 && s.votes.every((v) => connues.has(v.uid))
            && (s.ecran === 'jeu' || s.ecran === 'resultat')) setReprise(s);
        setDonnees(d);
      })
      .catch(() => setErreur(true));
  }, []);
  useEffect(() => {
    // Seuls les votes en cours et le résultat sont sauvegardés (l'accueil n'écrase rien)
    if (donnees && (ecran === 'jeu' || ecran === 'resultat'))
      ecrireSauvegarde({ ecran, votes, objectif, carte: carte?.uid ?? null, date: Date.now() });
  }, [donnees, ecran, votes, objectif, carte]);
  useEffect(() => { window.scrollTo(0, 0); }, [ecran]);

  const total = donnees?.cartes.length ?? 0;
  const progression = useMemo(() => Math.min(votes.length, objectif), [votes, objectif]);

  if (erreur) return <main className="ecran"><p>Impossible de charger les données. Vérifie ta connexion puis recharge la page.</p></main>;
  if (!donnees) return <main className="ecran chargement"><p>Chargement des votes…</p></main>;

  const reprendre = () => {
    if (!reprise) return;
    setVotes(reprise.votes);
    setObjectif(reprise.objectif);
    const c = donnees.cartes.find((x) => x.uid === reprise.carte) ?? carteSuivante(donnees, reprise.votes, lireVues());
    setCarte(c);
    setEcran(reprise.ecran === 'jeu' && c ? 'jeu' : 'resultat');
    setReprise(null);
  };

  const commencer = () => {
    setReprise(null);
    setVotes([]);
    setObjectif(SERIE);
    setImportant(false);
    setCarte(carteSuivante(donnees, [], lireVues()));
    setEcran('jeu');
  };

  const repondre = (r: Reponse) => {
    if (!carte) return;
    memoriserVue(carte.uid);
    const nouveaux = [...votes, { uid: carte.uid, reponse: r, important }];
    setVotes(nouveaux);
    setImportant(false);
    const suivante = nouveaux.length < objectif ? carteSuivante(donnees, nouveaux, lireVues()) : null;
    if (suivante) setCarte(suivante);
    else setEcran('resultat');
  };

  const continuer = () => {
    setObjectif(votes.length + RALLONGE);
    setCarte(carteSuivante(donnees, votes, lireVues()));
    setEcran('jeu');
  };

  const methode = () => { setRetour(ecran); setEcran('methode'); };

  return (
    <main>
      {ecran === 'accueil' && <Accueil donnees={donnees} reprise={reprise} onReprendre={reprendre} onCommencer={commencer} onMethode={methode} />}

      {ecran === 'jeu' && carte && (
        <section className="ecran jeu">
          <header className="barre-jeu">
            <button className="lien" onClick={() => {
              setReprise({ ecran: 'jeu', votes, objectif, carte: carte.uid, date: Date.now() });
              setEcran('accueil');
            }} aria-label="Quitter">✕</button>
            <div className="progression" aria-label={`Vote ${progression + 1} sur ${objectif}`}>
              <span style={{ width: `${(100 * progression) / objectif}%` }} />
            </div>
            <span className="compteur">{progression + 1}/{objectif}</span>
          </header>
          <p className="consigne">
            Le <strong>{dateVote(carte.date)}</strong>, votes-tu ce texte ?
          </p>
          <CarteSwipe
            key={carte.uid}
            carte={carte}
            important={important}
            onImportant={() => setImportant(!important)}
            onReponse={repondre}
          />
          {votes.length >= 5 && (
            <button className="lien terminer" onClick={() => setEcran('resultat')}>Voir mon résultat maintenant</button>
          )}
        </section>
      )}

      {ecran === 'resultat' && (
        <Resultat
          donnees={donnees}
          votes={votes}
          onContinuer={votes.length < total ? continuer : null}
          onRecommencer={commencer}
          onMethode={methode}
        />
      )}

      {ecran === 'methode' && <Methode donnees={donnees} onRetour={() => setEcran(retour)} />}
    </main>
  );
}
