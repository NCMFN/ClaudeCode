import subprocess
import sys

def main():
    print("Starting Enterprise Digital Sanitization Detection Pipeline...")

    phases = [
        ("Phase 1: Ingestion", "src/phase1_ingestion.py"),
        ("Phase 2: Feature Engineering", "src/phase2_features.py"),
        ("Phase 3: Modeling", "src/phase3_modeling.py"),
        ("Phase 4: Adversarial Testing", "src/phase4_adversarial.py"),
        ("Phase 5: Evaluation", "src/phase5_evaluation.py")
    ]

    for desc, script in phases:
        print(f"\n{'='*50}\nExecuting {desc}\n{'='*50}")
        try:
            subprocess.run([sys.executable, script], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Pipeline failed at {desc}. Exiting.")
            sys.exit(1)

    print("\nPipeline executed successfully.")

if __name__ == "__main__":
    main()
