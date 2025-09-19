# API V1 – Credit Scoring

Cette première version de l’API permet de tester le déploiement du modèle de scoring crédit pour "Prêt à dépenser".

## Fonctionnalités

- Chargement du modèle de scoring (`model_complet.pkl`)
- Endpoints de test pour vérifier le fonctionnement de l’API et du pipeline technique
- Génération de prédictions fictives à partir de données aléatoires

## Endpoints disponibles

- **GET /**  
  Statut de l’API, version, seuil optimal, informations sur le modèle.

- **GET /test_prediction**  
  Génère une prédiction aléatoire (pas de vrai client), retourne la probabilité de défaut et la décision (accepté/refusé).

- **GET /model_info**  
  Informations sur le modèle chargé (type, nombre de features, seuil, nom du modèle).

## Lancement de l’API

Depuis ce dossier :

```bash
python api_v1.py
```

L’API sera disponible sur [http://localhost:5003](http://localhost:5003).

## Limitations de la V1

- Pas de prédiction sur un vrai client à partir de son identifiant
- Pas de gestion avancée des erreurs
- API conçue pour des tests techniques et des démonstrations locales

--
