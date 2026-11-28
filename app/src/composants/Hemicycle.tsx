import { useMemo } from 'react';
import type { Groupe } from '../types';
import { placerSieges } from '../sieges';

interface Props {
  groupes: Groupe[];        // dans l'ordre usuel de l'hémicycle, de gauche à droite
  proches: Set<string>;     // groupe(s) le(s) plus proche(s)
}

export function Hemicycle({ groupes, proches }: Props) {
  const { sieges, monSiege } = useMemo(() => placerSieges(groupes, proches), [groupes, proches]);

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
