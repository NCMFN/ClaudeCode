import subprocess
import sys
import os

def main():
    print("Starting Enterprise Digital Sanitization Detection Pipeline...")

    phases = [
        ("Phase 1: Ingestion", "src/phase1_ingestion.py"),
        ("Phase 2: Feature Engineering", "src/phase2_features.py"),
        ("Phase 3: Modeling", "src/phase3_modeling.py"),
        ("Phase 4: Adversarial Testing", "src/phase4_adversarial.py"),
        ("Phase 5: Evaluation", "src/phase5_evaluation.py"),
        ("Phase 6: Artifacts", "src/phase6_artifacts.py")
    ]

    for desc, script in phases:
        print(f"\n{'='*50}\nExecuting {desc}\n{'='*50}")
        try:
            subprocess.run([sys.executable, script], check=True)

            if "Phase 1" in desc:
                if not os.path.exists("outputs/datasets/harmonized_events"):
                    print("\n[NOTE] Data acquisition failed (likely due to SSL strictness or missing local files).")
                    print("Halting pipeline execution gracefully to respect 'No Fabrication' constraints.")
                    sys.exit(0)

        except subprocess.CalledProcessError as e:
            print(f"Pipeline failed at {desc}. Exiting.")
            sys.exit(1)

    print("\nPipeline executed successfully. View results with 'python src/display_results.py'")

if __name__ == "__main__":
    main()
