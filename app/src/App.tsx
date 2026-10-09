import { useEffect, useMemo, useState } from 'react';
import type { Carte, Donnees, Reponse, Vote } from './types';
import { carteSuivante } from './score';
import { Accueil } from './composants/Accueil';
import { CarteSwipe } from './composants/CarteSwipe';
import { Resultat } from './composants/Resultat';
import { Methode } from './composants/Methode';

type Ecran = 'accueil' | 'jeu' | 'resultat' | 'methode';
const PARTIE = 15;
const RALLONGE = 10;

// Sauvegarde de la partie sur l'appareil : quitter la page (lien externe, rechargement) ne fait rien perdre
const CLE = 'depute-d-un-jour:partie';
interface Sauvegarde { ecran: Ecran; votes: Vote[]; objectif: number; carte: string | null; date?: number }
const DUREE_REPRISE = 2 * 60 * 60 * 1000; // une partie abandonnée depuis plus de 2 h repart de zéro

function lireSauvegarde(): Sauvegarde | null {
  try { return JSON.parse(localStorage.getItem(CLE) ?? 'null'); } catch { return null; }
}
function ecrireSauvegarde(s: Sauvegarde) {
  try { localStorage.setItem(CLE, JSON.stringify(s)); } catch { /* stockage indisponible : tant pis */ }
}

// Cartes vues lors des parties précédentes (pour proposer autre chose la fois suivante)
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
  const [objectif, setObjectif] = useState(PARTIE);
  const [carte, setCarte] = useState<Carte | null>(null);
  const [important, setImportant] = useState(false);

  useEffect(() => {
    charger()
      .then((d) => {
        const s = lireSauvegarde();
        const connues = new Set(d.cartes.map((c) => c.uid));
        // Seule une partie EN COURS et récente est reprise ; un résultat déjà vu n'est jamais rouvert
        const recente = s?.date && Date.now() - s.date < DUREE_REPRISE;
        if (s && recente && s.ecran === 'jeu' && s.votes.every((v) => connues.has(v.uid))) {
          setVotes(s.votes);
          setObjectif(s.objectif);
          const c = d.cartes.find((x) => x.uid === s.carte) ?? carteSuivante(d, s.votes, lireVues());
          setCarte(c);
          setEcran(c ? 'jeu' : 'resultat');
        }
        setDonnees(d);
      })
      .catch(() => setErreur(true));
  }, []);
  useEffect(() => {
    if (donnees && ecran !== 'methode') ecrireSauvegarde({ ecran, votes, objectif, carte: carte?.uid ?? null, date: Date.now() });
  }, [donnees, ecran, votes, objectif, carte]);
  useEffect(() => { window.scrollTo(0, 0); }, [ecran]);

  const total = donnees?.cartes.length ?? 0;
  const progression = useMemo(() => Math.min(votes.length, objectif), [votes, objectif]);

  if (erreur) return <main className="ecran"><p>Impossible de charger les données. Vérifie ta connexion puis recharge la page.</p></main>;
  if (!donnees) return <main className="ecran chargement"><p>Chargement des votes…</p></main>;

  const commencer = () => {
    setVotes([]);
    setObjectif(PARTIE);
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
      {ecran === 'accueil' && <Accueil donnees={donnees} onCommencer={commencer} onMethode={methode} />}

      {ecran === 'jeu' && carte && (
        <section className="ecran jeu">
          <header className="barre-jeu">
            <button className="lien" onClick={() => setEcran('accueil')} aria-label="Quitter">✕</button>
            <div className="progression" aria-label={`Vote ${progression + 1} sur ${objectif}`}>
              <span style={{ width: `${(100 * progression) / objectif}%` }} />
            </div>
            <span className="compteur">{progression + 1}/{objectif}</span>
          </header>
          <p className="consigne">Tu es député : votes-tu ce texte ?</p>
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
