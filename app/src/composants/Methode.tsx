import type { Donnees } from '../types';

export function Methode({ donnees, onRetour }: { donnees: Donnees; onRetour: () => void }) {
  return (
    <section className="ecran methode">
      <button className="lien retour" onClick={onRetour}>← Retour</button>
      <h1>Comment ça marche</h1>
      <p className="accroche">
        Une règle simple : <strong>ne rien inventer et ne rien choisir à la main</strong>.
        Tout vient des données publiques de l'Assemblée nationale, et chaque étape suit une règle écrite à l'avance.
      </p>

      <h2>1. Les votes</h2>
      <p>
        On part des {donnees.meta.scrutins_analyses.toLocaleString('fr-FR')} scrutins publics de la législature
        en cours. Pour chacun, on connaît le vote de chaque député. Un groupe a une position quand au moins
        80 % de ses voix exprimées vont dans le même sens. <strong>Une abstention ne compte jamais</strong>, et un groupe
        majoritairement abstentionniste n'a pas de position.
      </p>

      <h2>2. Le choix des cartes</h2>
      <p>
        Personne ne choisit les cartes. On garde d'abord tous les <strong>votes solennels</strong>, ceux que
        l'Assemblée désigne elle-même comme ses votes majeurs. Un algorithme ajoute ensuite les votes qui
        distinguent le mieux les groupes entre eux, avec une forte participation, sur des thèmes variés.
        Relancer le calcul donne exactement le même résultat.
      </p>

      <h2>3. Les votes ambigus</h2>
      <p>
        Parfois, un groupe vote contre une mesure… parce qu'il la trouve insuffisante. Pour ne pas fausser ton
        résultat, on lit ce que chaque groupe a déclaré dans l'hémicycle juste avant le vote. S'il dit
        explicitement soutenir l'objectif mais voter contre pour une autre raison, sa position n'est
        pas comptée sur cette carte. Chaque décision s'appuie sur une citation exacte, que tu peux lire.
      </p>

      <h2>4. Les résumés</h2>
      <p>
        Les textes de loi sont difficiles à lire. Une intelligence artificielle les résume avec des consignes
        strictes : faits uniquement, aucun argument, aucun nom de parti, rien sur le résultat du vote.
        Une seconde IA, indépendante, vérifie chaque carte en la comparant au texte officiel réellement voté.
        Chaque carte renvoie vers le texte, le scrutin et le débat officiels : tu peux tout vérifier.
      </p>

      <h2>5. Ton résultat</h2>
      <p>
        Pour chaque groupe : la part des cartes où il a voté comme toi, parmi celles où il avait une position.
        « Je ne sais pas » ne compte pas ; l'étoile fait compter une carte double. Deux groupes à moins de
        10 points d'écart sont présentés ex aequo. L'ordre des cartes s'adapte à tes réponses pour départager
        les groupes dont tu es proche.
      </p>

      <h2>Ce que l'appli ne fait pas</h2>
      <ul>
        <li>Elle ne te dit pas pour qui voter.</li>
        <li>Elle ne prédit pas les votes futurs.</li>
        <li>Elle ne collecte rien : aucun compte, aucun suivi.</li>
      </ul>

      <p className="note">
        Le code, la méthode détaillée, les consignes données à l'IA et toutes les données intermédiaires sont
        publics.{' '}
        {donnees.meta.depot && <a href={donnees.meta.depot} target="_blank" rel="noreferrer">Voir le projet</a>}
        {' '}· Données : Assemblée nationale, Licence Ouverte.
      </p>
    </section>
  );
}
