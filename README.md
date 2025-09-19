# API V3 – Credit Scoring

Cette version améliore la robustesse de l’API en ajoutant une gestion avancée des erreurs et des logs détaillés.

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

Depuis ce dossier :

```bash
python api_v3/app_v3.py
```

L’API sera disponible sur `http://localhost:5800`.

---

## Nouveautés de la V3

- Gestion avancée des erreurs (404, 500)
- Logs détaillés pour le debug et l’audit