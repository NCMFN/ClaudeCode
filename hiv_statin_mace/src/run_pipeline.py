import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from synthetic import generate_synthetic_data
import pandas as pd
from train import train_models
from evaluate import evaluate_models
from architecture import generate_architecture_diagram

if __name__ == '__main__':
    print("Generating synthetic data...")
    df = generate_synthetic_data()
    os.makedirs('../data/processed', exist_ok=True)
    df.to_csv('../data/processed/synthetic_data.csv', index=False)

    print("\nGenerating Architecture Diagram...")
    generate_architecture_diagram()

    print("\nTraining Models...")
    train_models()

    print("\nEvaluating Models...")
    evaluate_models()

    print("\nPipeline Complete!")
