import type { Groupe } from './types';

const RANGS = 12;
const R_MIN = 0.36;

export interface Siege { x: number; y: number; couleur: string; id: string; rang: number }

/** Sièges répartis en rangées concentriques (x de -1 à 1, y de 0 à 1), attribués aux groupes par angle croissant.
 *  « Ton siège » : au premier rang, au milieu du secteur du groupe le plus proche. Sert aussi à l'image de résultat. */
export function placerSieges(groupes: Groupe[], proches: Set<string>) {
  const total = groupes.reduce((s, g) => s + g.sieges, 0);
  const rayons = Array.from({ length: RANGS }, (_, i) => R_MIN + ((1 - R_MIN) * i) / (RANGS - 1));
  const somme = rayons.reduce((a, b) => a + b, 0);
  const pts: { x: number; y: number; angle: number; rang: number }[] = [];
  let reste = total;
  rayons.forEach((r, i) => {
    const n = i === RANGS - 1 ? reste : Math.round((total * r) / somme);
    reste -= n;
    for (let k = 0; k < n; k++) {
      const angle = Math.PI - (Math.PI * (k + 0.5)) / n;
      pts.push({ x: r * Math.cos(angle), y: r * Math.sin(angle), angle, rang: i });
    }
  });
  pts.sort((a, b) => b.angle - a.angle || a.rang - b.rang);
  const sieges: Siege[] = [];
  let k = 0;
  for (const g of groupes) for (let j = 0; j < g.sieges && k < pts.length; j++, k++)
    sieges.push({ ...pts[k], couleur: g.couleur, id: g.id });
  const secteur = sieges.filter((s) => proches.has(s.id) && s.rang === 0);
  return { sieges, monSiege: secteur[Math.floor(secteur.length / 2)] ?? null };
}
