import os
import glob

def count_artifacts():
    figures = glob.glob("outputs/figures/*")
    tables = glob.glob("outputs/tables/*")

    print("=== Artifact Count Verification ===")
    print(f"Total Figures: {len(figures)}")
    print(f"Total Tables: {len(tables)}")

    print("\nNet-New Figures (>20 baseline):", len(figures) - 20)
    print("Net-New Tables (>20 baseline):", len(tables) - 20)

    print("\nFigures:")
    for f in figures:
        print(f" - {f}")

    print("\nTables:")
    for t in tables:
        print(f" - {t}")

if __name__ == "__main__":
    count_artifacts()
