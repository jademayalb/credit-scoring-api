# API V2 – Credit Scoring

Cette version de l’API permet de faire une prédiction réelle sur un client à partir de son identifiant.

## Fonctionnalités

- Prédiction du risque de défaut pour un client donné (`client_id`)
- Prétraitement complet des données (encodage, features métier, gestion des valeurs manquantes)
- Utilisation du modèle de scoring entraîné

## Endpoints disponibles

- **GET /predict/<client_id>**  
  Retourne la probabilité de défaut, la décision (accepté/refusé), le seuil optimal, et le nom du modèle pour le client demandé.

## Lancement de l’API

Depuis ce dossier :

```bash
python api_v2.py
```

L’API sera disponible sur [http://localhost:5200](http://localhost:5200).

## Limitations de la V2

- Pas de gestion avancée des erreurs ou logs détaillés
