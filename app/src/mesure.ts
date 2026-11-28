// Mesure d'audience GoatCounter : seulement des étapes (début, résultat, partage), jamais une réponse ni un score.
declare global {
  interface Window { goatcounter?: { count?: (o: { path: string; title?: string; event?: boolean }) => void } }
}

export type Etape = 'commencer' | 'resultat' | 'rallonge' | 'partage-image' | 'partage-site';

export function compter(etape: Etape) {
  try { window.goatcounter?.count?.({ path: etape, event: true }); } catch { /* compteur bloqué : rien */ }
}
