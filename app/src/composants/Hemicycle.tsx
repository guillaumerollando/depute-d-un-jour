import { useMemo } from 'react';
import type { Groupe } from '../types';

interface Props {
  groupes: Groupe[];        // dans l'ordre usuel de l'hémicycle, de gauche à droite
  proches: Set<string>;     // groupe(s) le(s) plus proche(s)
}

const RANGS = 12;
const R_MIN = 0.36;

/** Hémicycle : sièges répartis en rangées concentriques, attribués aux groupes par angle croissant. */
export function Hemicycle({ groupes, proches }: Props) {
  const { sieges, monSiege } = useMemo(() => {
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
    const res: { x: number; y: number; couleur: string; id: string; rang: number }[] = [];
    let k = 0;
    for (const g of groupes) for (let j = 0; j < g.sieges && k < pts.length; j++, k++)
      res.push({ ...pts[k], couleur: g.couleur, id: g.id });
    // Ton siège : au premier rang, au milieu du secteur du groupe le plus proche
    const secteur = res.filter((s) => proches.has(s.id) && s.rang === 0);
    return { sieges: res, monSiege: secteur[Math.floor(secteur.length / 2)] ?? null };
  }, [groupes, proches]);

  const W = 200, H = 108, R = 98, cx = 100, cy = 102;
  return (
    <svg className="hemicycle" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Hémicycle de l'Assemblée nationale">
      {sieges.map((s, i) => (
        <circle
          key={i}
          cx={cx + s.x * R}
          cy={cy - s.y * R}
          r={2.1}
          fill={s.couleur}
          opacity={proches.size === 0 || proches.has(s.id) ? 1 : 0.22}
        />
      ))}
      {monSiege && (
        <g>
          <circle cx={cx + monSiege.x * R} cy={cy - monSiege.y * R} r={5.2} className="mon-siege" />
          <text x={cx + monSiege.x * R} y={cy - monSiege.y * R + 1.6} textAnchor="middle" className="mon-siege-txt">toi</text>
        </g>
      )}
    </svg>
  );
}
