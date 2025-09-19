import mlflow
import joblib
import os

mlflow.set_tracking_uri("file:/Users/jadesuchaud/Projet 7/mlruns")
print("MLflow Tracking URI :", mlflow.get_tracking_uri())

model = joblib.load("api_v3/artefacts/model.pkl")
print("Fichiers dans artefacts :", os.listdir("api_v3/artefacts"))

with mlflow.start_run(run_name="register_model_and_artefacts") as run:
    mlflow.sklearn.log_model(model, "model")
    mlflow.log_artifacts("api_v3/artefacts")
    model_uri = f"runs:/{run.info.run_id}/model"
    result = mlflow.register_model(model_uri, "CreditScoringModel")
    print(f"Modèle enregistré dans le Model Registry : {result.name} v{result.version}")

print("Accède à MLflow UI sur : http://127.0.0.1:5000/")