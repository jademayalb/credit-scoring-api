import os
from flask import Flask, jsonify
from joblib import load
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Chemin absolu pour les artefacts
BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "model_complet.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")
IMPUTER_PATH = os.path.join(BASE_DIR, "imputer.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "features.pkl")
TEST_CSV_PATH = os.path.join(BASE_DIR, "application_test.csv")

# Charger le modèle et les artefacts
try:
    model_data = load(MODEL_PATH)
    model = model_data['model']
    scaler = model_data['scaler']
    imputer = model_data['imputer']
    features = model_data['features']
    threshold = model_data['optimal_threshold']
    model_name = model_data['model_name']
    poly_transformer = model_data.get('poly_transformer', None)
    test_df = pd.read_csv(TEST_CSV_PATH)
    logging.info("Modèle et artefacts chargés avec succès.")
except Exception as e:
    logging.error(f"Erreur lors du chargement du modèle ou des artefacts : {e}")
    raise

def preprocess(df, features_model, poly_transformer=None):
    df = df.copy()
    le = LabelEncoder()
    for col in df.columns:
        if df[col].dtype == 'object':
            if len(df[col].unique()) <= 2:
                df[col] = le.fit_transform(df[col].astype(str))
    df = pd.get_dummies(df)
    if 'DAYS_EMPLOYED' in df.columns:
        df['DAYS_EMPLOYED_ANOM'] = df['DAYS_EMPLOYED'] == 365243
        df['DAYS_EMPLOYED'] = df['DAYS_EMPLOYED'].replace({365243: np.nan})
    for col in ['AMT_CREDIT', 'AMT_ANNUITY', 'AMT_INCOME_TOTAL', 'DAYS_BIRTH', 'DAYS_EMPLOYED']:
        if col not in df.columns:
            df[col] = np.nan
    df['CREDIT_INCOME_PERCENT'] = df['AMT_CREDIT'] / df['AMT_INCOME_TOTAL']
    df['ANNUITY_INCOME_PERCENT'] = df['AMT_ANNUITY'] / df['AMT_INCOME_TOTAL']
    df['CREDIT_TERM'] = df['AMT_ANNUITY'] / df['AMT_CREDIT']
    df['DAYS_EMPLOYED_PERCENT'] = df['DAYS_EMPLOYED'] / df['DAYS_BIRTH']
    if poly_transformer is not None:
        poly_cols = ['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3', 'DAYS_BIRTH']
        for col in poly_cols:
            if col not in df.columns:
                df[col] = np.nan
        poly_values = poly_transformer.transform(df[poly_cols])
        poly_feature_names = poly_transformer.get_feature_names_out(poly_cols)
        poly_df = pd.DataFrame(poly_values, columns=poly_feature_names, index=df.index)
        df = pd.concat([df, poly_df], axis=1)
    for col in features_model:
        if col not in df.columns:
            df[col] = 0
    df = df[features_model]
    return df

app = Flask(__name__)

@app.route('/predict/<int:client_id>', methods=['GET'])
def predict_client(client_id):
    try:
        client_row = test_df[test_df['SK_ID_CURR'] == client_id]
        if client_row.empty:
            logging.warning(f"Client ID {client_id} introuvable.")
            return jsonify({
                "erreur": f"Client ID {client_id} introuvable",
                "status": "NOT_FOUND"
            }), 404

        client_processed = preprocess(client_row, features, poly_transformer)
        X_imputed = imputer.transform(client_processed)
        X_scaled = scaler.transform(X_imputed)
        proba = model.predict_proba(X_scaled)[0, 1]
        decision = "REFUSÉ" if proba >= threshold else "ACCEPTÉ"

        logging.info(f"Prédiction réalisée pour client {client_id} : proba={proba:.4f}, décision={decision}")

        return jsonify({
            "client_id": int(client_id),
            "probabilite_defaut": float(proba),
            "seuil_optimal": float(threshold),
            "decision": decision,
            "model_name": model_name,
            "status": "OK"
        })
    except Exception as e:
        logging.error(f"Erreur interne lors de la prédiction pour client {client_id} : {e}")
        return jsonify({
            "erreur": "Erreur interne du serveur",
            "details": str(e),
            "status": "ERROR"
        }), 500

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Erreur 500 : {error}")
    return jsonify({"erreur": "Erreur interne du serveur"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5800)