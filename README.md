# API V3 – Credit Scoring

Cette version améliore la robustesse de l’API en ajoutant une gestion avancée des erreurs et des logs détaillés.

---

## Fonctionnalités

- Prédiction du risque de défaut pour un client donné (`client_id`)
- Prétraitement complet des données (encodage, features métier, gestion des valeurs manquantes)
- Utilisation du modèle de scoring entraîné
<<<<<<< HEAD

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
=======
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
## Nouveautés de la V3 :


Depuis ce dossier :

```
python api_v3.py
```

L’API sera disponible sur `http://localhost:5200`.

## Nouveautés de la V3 :

- Gestion avancée des erreurs (404, 500)
- Logs détaillés pour le debug et l’audit

>>>>>>> 6b491f8 (Ajout API V3 avec gestion avancée des erreurs et logs)
