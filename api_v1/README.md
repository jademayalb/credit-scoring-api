# API V1 - Credit Scoring

Cette API Flask permet de prédire le score de crédit d’un client.

## Lancement

```bash
python api_v1.py
```

## Endpoints

- `/predict/<client_id>` : Retourne la prédiction pour un client donné.

## Exemple d’appel

```bash
curl http://localhost:5000/predict/123456
```

## Limitations

- Cette version ne gère pas encore [ex : la gestion avancée des erreurs, l’explicabilité locale, etc.].
