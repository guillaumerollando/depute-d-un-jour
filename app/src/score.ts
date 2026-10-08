// Calcul du résultat et choix de la carte suivante — voir METHODE.md, section « Calcul du résultat ».
import type { Carte, Depute, Donnees, Groupe, ScoreGroupe, Vote } from './types';

export const EX_AEQUO = 10; // points de pourcentage

const poids = (v: Vote) => (v.important ? 2 : 1);

/** Accord avec chaque groupe : cartes où l'utilisateur et le groupe ont tous deux une position. */
export function scores(groupes: Groupe[], cartes: Map<string, Carte>, votes: Vote[]): ScoreGroupe[] {
  return groupes
    .map((groupe) => {
      let accord = 0, total = 0, n = 0;
      for (const v of votes) {
        if (v.reponse === 'passe') continue;
        const pos = cartes.get(v.uid)?.positions[groupe.id];
        if (!pos) continue;
        total += poids(v);
        n += 1;
        if (pos === v.reponse) accord += poids(v);
      }
      return { groupe, accord, total, cartes: n, pourcentage: total ? Math.round((100 * accord) / total) : null };
    })
    .sort((a, b) => (b.pourcentage ?? -1) - (a.pourcentage ?? -1) || b.cartes - a.cartes);
}

/** Regroupe les groupes dont les pourcentages diffèrent de moins de EX_AEQUO points du premier du paquet. */
export function paliers(liste: ScoreGroupe[]): ScoreGroupe[][] {
  const res: ScoreGroupe[][] = [];
  for (const s of liste.filter((s) => s.pourcentage !== null)) {
    const dernier = res[res.length - 1];
    if (dernier && (dernier[0].pourcentage! - s.pourcentage!) < EX_AEQUO) dernier.push(s);
    else res.push([s]);
  }
  return res;
}

function melanger<T>(t: T[]): T[] {
  const a = [...t];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

const PREMIERES_CARTES = 4;

/**
 * Carte suivante :
 * - les premières cartes viennent du socle des votes solennels, sur des thèmes tous différents ;
 * - ensuite, la carte qui départage le plus de paires parmi les groupes encore en tête.
 * Un vote solennel vaut un départage et demi de plus : une carte mineure ne passe devant que si elle
 * départage nettement mieux. À égalité, le hasard (pour varier les parties).
 */
export function carteSuivante(d: Donnees, votes: Vote[]): Carte | null {
  const vues = new Set(votes.map((v) => v.uid));
  const restantes = melanger(d.cartes.filter((c) => !vues.has(c.uid)));
  if (!restantes.length) return null;

  if (votes.length < PREMIERES_CARTES) {
    const themesVus = new Set(votes.map((v) => d.cartes.find((c) => c.uid === v.uid)?.theme));
    return (
      restantes.find((c) => c.socle && !themesVus.has(c.theme)) ??
      restantes.find((c) => !themesVus.has(c.theme)) ??
      restantes[0]
    );
  }

  const index = new Map(d.cartes.map((c) => [c.uid, c]));
  const liste = scores(d.groupes, index, votes).filter((s) => s.pourcentage !== null);
  const meilleur = liste[0]?.pourcentage ?? 0;
  // Groupes « encore en tête » : à moins de 20 points du premier ; au moins trois groupes
  let tete = liste.filter((s) => meilleur - (s.pourcentage ?? 0) < 20).map((s) => s.groupe.id);
  if (tete.length < 3) tete = liste.slice(0, 3).map((s) => s.groupe.id);

  let choix: Carte | null = null, gainMax = -1;
  for (const c of restantes) {
    let gain = 0;
    for (let i = 0; i < tete.length; i++)
      for (let j = i + 1; j < tete.length; j++) {
        const a = c.positions[tete[i]], b = c.positions[tete[j]];
        if (a && b && a !== b) gain += 1;
      }
    const score = gain * 2 + (c.socle ? 3 : 0);
    if (score > gainMax) { gainMax = score; choix = c; }
  }
  return choix;
}

/** Député dont les votes ressemblent le plus aux tiens : il doit avoir voté sur au moins 60 % de tes cartes
 *  (et au moins 5), pour qu'un député peu présent ne gagne pas par hasard. */
export function deputeJumeau(deputes: Depute[], cartes: Map<string, Carte>, votes: Vote[]) {
  const acc = new Map<number, { accord: number; total: number }>();
  for (const v of votes) {
    if (v.reponse === 'passe') continue;
    const c = cartes.get(v.uid);
    if (!c) continue;
    for (const [pos, liste] of [['pour', c.deputes.p], ['contre', c.deputes.c]] as const)
      for (const i of liste) {
        const e = acc.get(i) ?? { accord: 0, total: 0 };
        e.total += poids(v);
        if (pos === v.reponse) e.accord += poids(v);
        acc.set(i, e);
      }
  }
  const repondu = votes.filter((v) => v.reponse !== 'passe').reduce((s, v) => s + poids(v), 0);
  const minimum = Math.max(5, Math.ceil(0.6 * repondu));
  let best: { depute: Depute; pourcentage: number; total: number } | null = null;
  for (const [i, e] of acc) {
    if (e.total < minimum) continue;
    const p = Math.round((100 * e.accord) / e.total);
    if (!best || p > best.pourcentage || (p === best.pourcentage && e.total > best.total))
      best = { depute: deputes[i], pourcentage: p, total: e.total };
  }
  return best;
}
