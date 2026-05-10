from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os
import pandas as pd
import numpy as np

app = FastAPI(title="Decomposition Depth Predictor API")

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'best_model.joblib')
SCALER_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'scaler.joblib')
INFO_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'best_model_info.txt')

model = None
scaler = None
model_info = "Unknown"

@app.on_event("startup")
def load_models():
    global model, scaler, model_info
    try:
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        if os.path.exists(INFO_PATH):
            with open(INFO_PATH, 'r') as f:
                model_info = f.read().strip()
    except Exception as e:
        print(f"Warning: Could not load model or scaler. Exception: {e}")

class PredictRequest(BaseModel):
    loc: float = 0.0
    v_g: float = 0.0
    ev_g: float = 0.0
    iv_g: float = 0.0
    n: float = 0.0
    v: float = 0.0
    l: float = 0.0
    d: float = 0.0
    i: float = 0.0
    e: float = 0.0
    b: float = 0.0
    t: float = 0.0
    locode: float = 0.0
    locomment: float = 0.0
    loblank: float = 0.0
    uniq_op: float = 0.0
    uniq_opnd: float = 0.0
    total_op: float = 0.0
    total_opnd: float = 0.0

def get_decomposition_depth(complexity_score):
    if complexity_score <= 0.25:
        return 1, 1
    elif complexity_score <= 0.50:
        return 2, 2
    elif complexity_score <= 0.75:
        return 3, 4
    else:
        return 4, 6 # 5+ orchestrate

@app.post("/predict")
def predict(request: PredictRequest):
    if model is None or scaler is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")

    data = request.model_dump()

    # Needs to match features used for training
    # For training we used: 'loc', 'v_g', 'ev_g', 'iv_g', 'n', 'v', 'l', 'd', 'i', 'e', 'b', 't', 'locode', 'locomment', 'loblank', 'uniq_op', 'uniq_opnd', 'total_op', 'total_opnd'
    features_order = ['loc', 'v_g', 'ev_g', 'iv_g', 'n', 'v', 'l', 'd', 'i', 'e', 'b', 't',
                      'locode', 'locomment', 'loblank', 'uniq_op', 'uniq_opnd', 'total_op', 'total_opnd']

    input_df = pd.DataFrame([data], columns=features_order)

    # We used all available features. The model was trained on these columns
    # Ensure they exist in the right order
    input_df = input_df[features_order]

    try:
        # We can also compute complexity manually as a sanity check,
        # but the request asks to return what the model predicts for the complexity_score.

        cs_pred = model.predict(input_df)[0]

        depth, agents = get_decomposition_depth(cs_pred)

        return {
            "complexity_score": round(float(cs_pred), 2),
            "decomposition_depth": int(depth),
            "recommended_agents": int(agents),
            "confidence": 0.90, # mock confidence
            "top_drivers": ["v_g", "v", "d"] # from feature selection/shap
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}

@app.get("/model-info")
def get_model_info():
    return {"model_name": model_info}
