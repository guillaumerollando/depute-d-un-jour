// Partage du site : feuille de partage du système, sinon lien copié. On partage le test, jamais un résultat.
const TEXTE = "Député d'un jour : vote sur de vrais textes de l'Assemblée nationale et découvre de quels groupes tu es le plus proche.";

/** Renvoie true si le lien a été copié (pas de feuille de partage), false sinon. */
export async function partagerSite(): Promise<boolean> {
  const url = `${location.origin}${import.meta.env.BASE_URL}`;
  try {
    if (navigator.share) { await navigator.share({ title: "Député d'un jour", text: TEXTE, url }); return false; }
    await navigator.clipboard.writeText(`${TEXTE} ${url}`);
    return true;
  } catch { return false; /* partage annulé ou presse-papiers refusé */ }
}
