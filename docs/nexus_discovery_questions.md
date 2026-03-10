# Nexus: Questions levée de doute (Transition API)

Pour transformer le "bijou" actuel en une infrastructure Cloud-Native scalable, voici les points flous à éclaircir. Répondre à ces questions nous permettra de définir le périmètre de la **Phase 1 (MVP)**.

## 1. Vision & Scope (Périmètre)
- **MVP Dashboard :** On commence par une API pure (utilisable via CLI/Agents) ou est-ce qu'on veut dès le jour 1 une interface web (Next.js) pour visualiser ses missions ?
- **Public vs Privé :** Est-ce que le catalogue de skills doit être public par défaut (type Registry) avec des options privées, ou un système 100% privé pour entreprises ?

## 2. Identité & Authentification (Auth)
- **Login Agent-Native :** Pour que Claude Code ou Cursor puissent appeler l'API Nexus, quelle méthode préfères-tu ?
  - A. **OAuth GitHub** (Le plus naturel pour les devs).
  - B. **Magic Links** (Email).
  - C. **API Keys** générées manuellement depuis un dashboard.

## 3. Gestion des Données (Storage)
- **Hébergement des Skills :** L'API Nexus doit-elle :
  - A. Être un **Proxy** qui lit les fichiers sur GitHub (aiskills-repo).
  - B. Être une **Base de données** qui stocke ses propres versions des skills pour plus de rapidité ?

## 4. Business & Monétisation (Paiement)
- **Paywall :** Comment imagines-tu le déclencheur de la facturation ?
  - À l'installation d'une skill premium ?
  - Au nombre de missions orchestrées / mois ?
  - Via une souscription fixe (SaaS) ?
- **Processeur :** On part sur du **Stripe** standard ou une solution plus spécifique au monde AI ?

## 5. Expérience Utilisateur (UX)
- **Agent Integration :** Veux-tu qu'on développe un "Plugin" spécifique pour Claude Code, ou on reste sur l'approche actuelle où le CLI fait le pont ?

---
**Lionel, dis-moi ce qui résonne le plus avec ta vision pour Nümtema AI FOUNDRY.**
