// Image du résultat, à partager sur les réseaux (format portrait 4:5, lisible en story comme sur LinkedIn).
// Tout est dessiné sur l'appareil : rien n'est envoyé, l'image n'existe que si la personne la demande.
import type { Groupe, ScoreGroupe } from './types';
import type { Melange } from './score';
import { placerSieges } from './sieges';

export interface ContenuImage {
  groupes: Groupe[];
  premiers: ScoreGroupe[];
  repondus: number;
  melange: Melange[];
  assemblee: { pourcentage: number } | null;
}

const L = 1080, H = 1350, MARGE = 80;
const MARINE = '#1d2b4f', OR = '#c8912c', OR_CLAIR = '#e8b04a', PAPIER = '#f4f5f8', DOUX = '#55607a', TRAIT = '#dfe3ec';
const TITRE = "'Archivo Variable', 'Arial Narrow', Arial, sans-serif";
const TEXTE = "'Public Sans Variable', system-ui, Arial, sans-serif";

/** Coupe un texte en lignes qui tiennent dans la largeur donnée. */
function lignes(ctx: CanvasRenderingContext2D, texte: string, largeur: number): string[] {
  const res: string[] = [];
  let ligne = '';
  for (const mot of texte.split(' ')) {
    const essai = ligne ? `${ligne} ${mot}` : mot;
    if (ctx.measureText(essai).width > largeur && ligne) { res.push(ligne); ligne = mot; } else ligne = essai;
  }
  if (ligne) res.push(ligne);
  return res;
}

function liste(noms: string[]) {
  return noms.length <= 1 ? noms.join('') : `${noms.slice(0, -1).join(', ')} et ${noms[noms.length - 1]}`;
}

function arcs(ctx: CanvasRenderingContext2D, x: number, y: number, e: number) {
  ctx.save();
  ctx.strokeStyle = OR_CLAIR; ctx.lineWidth = 4 * e; ctx.lineCap = 'round';
  for (const r of [28, 18, 8]) { ctx.beginPath(); ctx.arc(x, y, r * e, Math.PI, 0); ctx.stroke(); }
  ctx.restore();
}

export async function dessinerResultat(c: ContenuImage): Promise<Blob> {
  // Les polices du site doivent être chargées avant de dessiner, sinon le canvas prend une police de secours
  try { await Promise.all([document.fonts.load(`800 72px ${TITRE}`), document.fonts.load(`400 32px ${TEXTE}`), document.fonts.load(`700 32px ${TEXTE}`)]); } catch { /* police de secours */ }

  const canvas = document.createElement('canvas');
  canvas.width = L; canvas.height = H;
  const ctx = canvas.getContext('2d')!;
  ctx.fillStyle = PAPIER; ctx.fillRect(0, 0, L, H);

  // Bandeau du haut
  ctx.fillStyle = MARINE; ctx.fillRect(0, 0, L, 150);
  arcs(ctx, MARGE + 30, 98, 1.25);
  ctx.fillStyle = '#ffffff'; ctx.font = `800 50px ${TITRE}`; ctx.textBaseline = 'alphabetic';
  ctx.fillText("Député d'un jour", MARGE + 90, 96);

  // Phrase principale
  let y = 245;
  ctx.fillStyle = OR; ctx.font = `700 30px ${TEXTE}`;
  ctx.fillText("J'AI VOTÉ COMME", MARGE, y);
  y += 20;
  const noms = c.premiers.map((s) => s.groupe.nom);
  let taille = 68;
  let texte = liste(noms);
  ctx.font = `800 ${taille}px ${TITRE}`;
  let ls = lignes(ctx, texte, L - 2 * MARGE);
  if (ls.length > 3) { texte = liste(c.premiers.map((s) => s.groupe.sigle)); ls = lignes(ctx, texte, L - 2 * MARGE); }
  if (ls.length > 2) { taille = 56; ctx.font = `800 ${taille}px ${TITRE}`; ls = lignes(ctx, texte, L - 2 * MARGE); }
  ctx.fillStyle = MARINE;
  for (const l of ls.slice(0, 3)) { y += taille * 1.08; ctx.fillText(l, MARGE, y); }
  y += 58;
  ctx.font = `400 34px ${TEXTE}`; ctx.fillStyle = DOUX;
  const pc = c.premiers[0]?.pourcentage ?? 0;
  ctx.fillText(`dans ${pc} % des cas, sur ${c.repondus} votes réels de l'Assemblée`, MARGE, y);
  if (c.premiers.length > 1) { y += 40; ctx.font = `400 26px ${TEXTE}`; ctx.fillText('(ex aequo : moins de 10 points d’écart)', MARGE, y); }

  // Hémicycle
  const proches = new Set(c.premiers.map((s) => s.groupe.id));
  const { sieges, monSiege } = placerSieges(c.groupes, proches);
  const R = 330, cx = L / 2;
  const cy = y + 40 + R;
  for (const s of sieges) {
    ctx.globalAlpha = proches.has(s.id) ? 1 : 0.2;
    ctx.fillStyle = s.couleur;
    ctx.beginPath(); ctx.arc(cx + s.x * R, cy - s.y * R, 7.2, 0, 2 * Math.PI); ctx.fill();
  }
  ctx.globalAlpha = 1;
  if (monSiege) {
    const mx = cx + monSiege.x * R, my = cy - monSiege.y * R;
    ctx.fillStyle = PAPIER; ctx.strokeStyle = MARINE; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.arc(mx, my, 22, 0, 2 * Math.PI); ctx.fill(); ctx.stroke();
    ctx.fillStyle = MARINE; ctx.font = `800 17px ${TEXTE}`; ctx.textAlign = 'center';
    ctx.fillText('moi', mx, my + 6); ctx.textAlign = 'left';
  }
  y = cy + 70;

  // Mélange par famille de thèmes
  if (c.melange.length) {
    ctx.fillStyle = OR; ctx.font = `700 26px ${TEXTE}`;
    ctx.fillText('MON MÉLANGE', MARGE, y);
    y += 14;
    for (const m of c.melange) {
      y += 52;
      ctx.strokeStyle = TRAIT; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(MARGE, y - 38); ctx.lineTo(L - MARGE, y - 38); ctx.stroke();
      ctx.fillStyle = DOUX; ctx.font = `400 29px ${TEXTE}`;
      ctx.fillText(m.famille, MARGE, y);
      // Sigles alignés à droite, chacun précédé de sa pastille de couleur
      ctx.font = `700 29px ${TEXTE}`;
      const sigles = m.premiers.slice(0, 3).map((s) => s.groupe);
      const plus = m.premiers.length > 3 ? ` +${m.premiers.length - 3}` : '';
      let x = L - MARGE;
      if (plus) { ctx.fillStyle = DOUX; ctx.textAlign = 'right'; ctx.fillText(plus, x, y); x -= ctx.measureText(plus).width + 8; }
      for (const g of [...sigles].reverse()) {
        ctx.fillStyle = MARINE; ctx.textAlign = 'right'; ctx.fillText(g.sigle, x, y);
        x -= ctx.measureText(g.sigle).width + 14;
        ctx.fillStyle = g.couleur; ctx.beginPath(); ctx.roundRect(x - 18, y - 22, 18, 18, 4); ctx.fill();
        x -= 36;
      }
      ctx.textAlign = 'left';
    }
    y += 30;
  }

  if (c.assemblee) {
    y += 34;
    ctx.fillStyle = MARINE; ctx.font = `400 29px ${TEXTE}`;
    const phrase = `J'ai voté comme la majorité de l'Assemblée sur ${c.assemblee.pourcentage} % des textes.`;
    for (const l of lignes(ctx, phrase, L - 2 * MARGE)) { ctx.fillText(l, MARGE, y); y += 40; }
  }

  // Bandeau du bas : l'invitation
  ctx.fillStyle = MARINE; ctx.fillRect(0, H - 120, L, 120);
  ctx.fillStyle = '#ffffff'; ctx.font = `700 34px ${TEXTE}`;
  ctx.fillText('Et toi ?', MARGE, H - 50);
  ctx.fillStyle = OR_CLAIR; ctx.font = `800 40px ${TITRE}`; ctx.textAlign = 'right';
  ctx.fillText('deputedunjour.fr', L - MARGE, H - 48);
  ctx.textAlign = 'left';

  return new Promise((ok, ko) => canvas.toBlob((b) => (b ? ok(b) : ko(new Error('image'))), 'image/png'));
}
