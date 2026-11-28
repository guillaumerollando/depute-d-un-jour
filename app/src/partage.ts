// Partage : le site (feuille de partage du système, sinon lien copié), ou l'image du résultat si la personne la demande.
import { compter } from './mesure';

const TEXTE = "Député d'un jour : vote sur de vrais textes de l'Assemblée nationale et découvre de quels groupes tu es le plus proche.";
const url = () => `${location.origin}${import.meta.env.BASE_URL}`;

/** Renvoie true si le lien a été copié (pas de feuille de partage), false sinon. */
export async function partagerSite(): Promise<boolean> {
  compter('partage-site');
  try {
    if (navigator.share) { await navigator.share({ title: "Député d'un jour", text: TEXTE, url: url() }); return false; }
    await navigator.clipboard.writeText(`${TEXTE} ${url()}`);
    return true;
  } catch { return false; /* partage annulé ou presse-papiers refusé */ }
}

export const NOM_IMAGE = 'mon-resultat-depute-d-un-jour.png';

/** Partage l'image avec la feuille de partage du système quand elle accepte les fichiers.
 *  Renvoie false si ce n'est pas possible : il reste alors le bouton « Enregistrer l'image ». */
export async function partagerImage(image: Blob): Promise<boolean> {
  const fichier = new File([image], NOM_IMAGE, { type: 'image/png' });
  if (!navigator.canShare?.({ files: [fichier] })) return false;
  compter('partage-image');
  try { await navigator.share({ files: [fichier], text: `Et toi ? ${url()}` }); } catch { /* partage annulé */ }
  return true;
}
