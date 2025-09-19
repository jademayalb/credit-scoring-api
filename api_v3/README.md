# API V4 – Credit Scoring

Cette version V4 corrige plusieurs problèmes de robustesse et d’organisation rencontrés en V3, tout en conservant la gestion avancée des erreurs et les logs détaillés.

---

## Fonctionnalités

- Prédiction du risque de défaut pour un client donné (`client_id`)
- Prétraitement complet des données (encodage, features métier, gestion des valeurs manquantes)
- Utilisation du modèle de scoring entraîné
- **Gestion avancée des erreurs** : messages explicites pour les cas d’ID inexistant ou d’erreur interne
- **Logs détaillés** : toutes les étapes importantes et erreurs sont loguées dans la console

---

## Endpoints disponibles

### **GET** `/predict/<client_id>`

Retourne :
- La probabilité de défaut
- La décision (**accepté/refusé**)
- Le seuil optimal
- Le nom du modèle utilisé

En cas d’erreur (ID inexistant, problème interne), un message explicite et un code HTTP adapté sont retournés (`404`, `500`).

---

## Lancement de l’API

Depuis ce dossier :

```bash
python api.py
```

L’API sera disponible sur `http://localhost:5800`.

---

## Nouveautés et corrections de la V4

- **Correction de la gestion des chemins** : tous les artefacts (modèle, scaler, imputer, CSV…) sont chargés via des chemins absolus robustes, évitant les erreurs de chargement selon l’endroit d’où l’API est lancée.
- **Organisation des artefacts** : plus de clarté et de modularité dans le chargement des fichiers.
- **Requirements améliorés** : le fichier `requirements.txt` a été revu pour garantir la compatibilité et l’installation rapide de toutes les dépendances nécessaires.
- **Robustesse accrue** : gestion des erreurs de chargement dès le démarrage, logs plus explicites.
- **Fonctionnalités et endpoints inchangés** : la compatibilité avec les usages de la V3 est assurée.

---

## Passage à la V4

Pour versionner cette release :

```bash
git tag v4.0
git push origin v4.0
```