from flask import Flask, jsonify, request
import joblib
import numpy as np

# Créer l'application Flask
app = Flask(__name__)

print("Démarrage de l'API...")

# Charger le modèle au démarrage
try:
    model_data = joblib.load("model_complet.pkl")
    print("Modèle chargé avec succès")
    print(f"Seuil optimal : {model_data.get('optimal_threshold', 0.52)}")
except Exception as e:
    print(f"Erreur chargement modèle: {e}")
    model_data = None

# Route de base pour tester que l'API fonctionne
@app.route('/')
def accueil():
    return jsonify({
        "message": "API Scoring Crédit v1.0 - Simple",
        "status": "OK",
        "version": "1.0",
        "modele_charge": model_data is not None,
        "seuil_optimal": float(model_data['optimal_threshold']) if model_data else 0.52,
        "description": "API simple avec données aléatoires pour test"
    })

# Route pour une prédiction bidon (test)
@app.route('/test_prediction')
def test_prediction():
    if model_data is None:
        return jsonify({"erreur": "Modèle non chargé"}), 500
    
    try:
        # Créer des données bidon pour tester
        donnees_bidon = np.random.rand(1, len(model_data['features']))
        
        # Faire le preprocessing
        donnees_preprocessed = model_data['scaler'].transform(
            model_data['imputer'].transform(donnees_bidon)
        )
        
        # Prédiction
        probabilite = model_data['model'].predict_proba(donnees_preprocessed)[0, 1]
        seuil = model_data['optimal_threshold']
        
        return jsonify({
            "message": "Test de prédiction réussi !",
            "probabilite_defaut": float(probabilite),
            "seuil_optimal": float(seuil),
            "decision": "REFUSÉ" if probabilite >= seuil else "ACCEPTÉ",
            "version": "1.0",
            "type": "test_aleatoire"
        })
        
    except Exception as e:
        return jsonify({
            "erreur": f"Problème lors de la prédiction: {str(e)}"
        }), 500

# Route d'information sur le modèle
@app.route('/model_info')
def model_info():
    if model_data is None:
        return jsonify({"erreur": "Modèle non chargé"}), 500
    
    return jsonify({
        "model_type": str(type(model_data['model'])),
        "nb_features": len(model_data['features']),
        "seuil_optimal": float(model_data['optimal_threshold']),
        "model_name": model_data.get('model_name', 'Unknown'),
        "version": "1.0"
    })

# Lancer l'API sur le port 5003
if __name__ == '__main__':
    print("API disponible sur: http://localhost:5003")
    print("Endpoints disponibles:")
    print("  - GET /              : Status API")
    print("  - GET /test_prediction : Test avec données aléatoires")
    print("  - GET /model_info    : Informations modèle")
    app.run(debug=True, port=5003)
