import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from joblib import load
from sklearn.preprocessing import LabelEncoder

# Charger le dictionnaire complet
model_data = load("model_complet.pkl")
model = model_data['model']
scaler = model_data['scaler']
imputer = model_data['imputer']
features = model_data['features']
threshold = model_data['optimal_threshold']
model_name = model_data['model_name']

# Charger le poly_transformer 
try:
    poly_transformer = model_data['poly_transformer']
except KeyError:
    poly_transformer = None

# Charger le jeu de test
test_df = pd.read_csv("application_test.csv")

# Fonction de prétraitement
def preprocess(df, features_model, poly_transformer=None):
    df = df.copy()

    # Encodage LabelEncoder pour les colonnes binaires
    le = LabelEncoder()
    for col in df.columns:
        if df[col].dtype == 'object':
            if len(df[col].unique()) <= 2:
                df[col] = le.fit_transform(df[col].astype(str))

    # One-hot encoding
    df = pd.get_dummies(df)

    # Gestion de l’anomalie DAYS_EMPLOYED
    if 'DAYS_EMPLOYED' in df.columns:
        df['DAYS_EMPLOYED_ANOM'] = df['DAYS_EMPLOYED'] == 365243
        df['DAYS_EMPLOYED'] = df['DAYS_EMPLOYED'].replace({365243: np.nan})

    # Création des variables métier
    for col in ['AMT_CREDIT', 'AMT_ANNUITY', 'AMT_INCOME_TOTAL', 'DAYS_BIRTH', 'DAYS_EMPLOYED']:
        if col not in df.columns:
            df[col] = np.nan
    df['CREDIT_INCOME_PERCENT'] = df['AMT_CREDIT'] / df['AMT_INCOME_TOTAL']
    df['ANNUITY_INCOME_PERCENT'] = df['AMT_ANNUITY'] / df['AMT_INCOME_TOTAL']
    df['CREDIT_TERM'] = df['AMT_ANNUITY'] / df['AMT_CREDIT']
    df['DAYS_EMPLOYED_PERCENT'] = df['DAYS_EMPLOYED'] / df['DAYS_BIRTH']

    # (Optionnel) Ajout des features polynomiales
    if poly_transformer is not None:
        poly_cols = ['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3', 'DAYS_BIRTH']
        for col in poly_cols:
            if col not in df.columns:
                df[col] = np.nan
        poly_values = poly_transformer.transform(df[poly_cols])
        poly_feature_names = poly_transformer.get_feature_names_out(poly_cols)
        poly_df = pd.DataFrame(poly_values, columns=poly_feature_names, index=df.index)
        df = pd.concat([df, poly_df], axis=1)

    # Alignement des colonnes avec le modèle
    for col in features_model:
        if col not in df.columns:
            df[col] = 0
    df = df[features_model]

    return df

# Création de l'app Flask
app = Flask(__name__)

@app.route('/predict/<int:client_id>', methods=['GET'])
def predict_client(client_id):
    client_row = test_df[test_df['SK_ID_CURR'] == client_id]
    if client_row.empty:
        return jsonify({"erreur": f"Client ID {client_id} introuvable"}), 404

    # Prétraitement
    client_processed = preprocess(client_row, features, poly_transformer)

    # Imputation + scaling
    X_imputed = imputer.transform(client_processed)
    X_scaled = scaler.transform(X_imputed)

    # Prédiction
    proba = model.predict_proba(X_scaled)[0, 1]
    decision = "REFUSÉ" if proba >= threshold else "ACCEPTÉ"

    return jsonify({
        "client_id": int(client_id),
        "probabilite_defaut": float(proba),
        "seuil_optimal": float(threshold),
        "decision": decision,
        "model_name": model_name,
        "status": "OK"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5200)