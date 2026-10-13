from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEPLOY_MODEL = ROOT / "models" / "healthguard_model.deploy.joblib"
LOCAL_MODEL = ROOT / "models" / "healthguard_model.joblib"
MODEL_PATH = DEPLOY_MODEL if DEPLOY_MODEL.exists() else LOCAL_MODEL
MODEL = None


def _get_model():
    """Load the model only when a prediction is first requested."""
    global MODEL
    if MODEL is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model file not found at {MODEL_PATH}. Restore the deployment model artifact."
            )
        MODEL = joblib.load(MODEL_PATH)
    return MODEL

def predict(row: dict, top_k=3):
    model = _get_model()
    X = pd.DataFrame([row])
    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0]
    classes = model.classes_
    ranked = sorted(zip(classes, proba), key=lambda x: x[1], reverse=True)
    top = ranked if top_k is None else ranked[:top_k]
    return pred, [(c, float(p)) for c,p in top]
