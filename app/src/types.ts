export type Position = 'pour' | 'contre';
export type Reponse = Position | 'passe';

export interface Groupe {
  id: string;          // clé interne : LFI, GDR, ECOS…
  sigle: string;       // sigle officiel affiché
  nom: string;         // nom officiel complet
  couleur: string;     // couleur officielle fournie par l'Assemblée
  sieges: number;
}

export interface Citation {
  orateur: string | null;
  citation: string;
  categorie: 'A' | 'B';
}

export interface Carte {
  uid: string;
  numero: number;
  date: string;
  type: string;
  socle: boolean;
  theme: string;
  titre: string;
  ce_que_ca_change: string;
  contexte: string;
  resultat: string;
  positions: Record<string, Position>;
  neutralises: string[];
  citations: Record<string, Citation>;
  liens: { scrutin: string; dossier: string; texte: string | null; compte_rendu: string | null };
  deputes: { p: number[]; c: number[] };
}

export interface Depute {
  nom: string;
  groupe: string;
  departement: string | null;
}

export interface Meta {
  date_donnees: string;
  scrutins_analyses: number;
  cartes: number;
  depot: string;
}

export interface Donnees {
  groupes: Groupe[];
  cartes: Carte[];
  deputes: Depute[];
  meta: Meta;
}

export interface Vote {
  uid: string;
  reponse: Reponse;
  important: boolean;
}

export interface ScoreGroupe {
  groupe: Groupe;
  accord: number;     // somme des poids en accord
  total: number;      // somme des poids comparables
  cartes: number;     // nombre de cartes comparables
  pourcentage: number | null;
}
