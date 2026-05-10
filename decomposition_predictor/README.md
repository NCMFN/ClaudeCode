# Predicting Software Project Decomposition Depth

This project builds a supervised regression pipeline to predict the optimal "decomposition depth" (number of required sub-agents/modules) for a software task based on static code complexity metrics (McCabe and Halstead features). This predictor serves as a lightweight pre-action classifier before launching complex LLM Multi-Agent systems.

## Datasets
The primary dataset used is the NASA Metrics Data Program (MDP) fetched seamlessly via OpenML. It incorporates modules from several mission-critical software projects including JM1, PC1, KC1, etc.

## Setup Instructions

1. **Environment Setup**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2. **Run Pipeline**
    To execute the entire pipeline end-to-end, execute the following commands in order:
    ```bash
    python src/ingest.py        # Downloads the raw dataset
    python src/preprocess.py    # Engineers the target variable
    python src/eda.py           # Generates Exploratory Data Analysis plots
    python src/train.py         # Feature Selection & Model Training
    python src/evaluate.py      # Final metrics, cross-domain test, and SHAP
    ```

3. **Running the API**
    Start the FastAPI inference microservice:
    ```bash
    uvicorn src.api:app --reload
    ```
    Alternatively, build and run via Docker:
    ```bash
    docker build -t decomp-predictor .
    docker run -p 8000:8000 decomp-predictor
    ```

## API Usage

The API provides a `/predict` endpoint to predict decomposition depth given source code metrics.

**Request:**
```bash
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -d '{
  "loc": 450,
  "v_g": 12,
  "ev_g": 8,
  "iv_g": 6,
  "v": 3200,
  "l": 0.04,
  "d": 25.0,
  "e": 80000,
  "b": 1.07
}'
```

**Response:**
```json
{
  "complexity_score": 0.03,
  "decomposition_depth": 1,
  "recommended_agents": 1,
  "confidence": 0.9,
  "top_drivers": ["v_g", "v", "d"]
}
```

## Results
Please review the `results/report.md` for in-depth insights into feature selection, cross-domain generalization, and the Random Forest model's performance on predicting software decomposition.
