import phase1_ingestion
import phase2_features
import phase3_modeling
import phase4_adversarial
import phase5_sampling_viz
import phase6_artifacts

def run():
    print("Starting pipeline...")
    df = phase1_ingestion.ingest_data()
    df = phase2_features.engineer_features(df)

    splits = phase3_modeling.split_data(df)

    ablation, preds_store = phase3_modeling.run_ablation(df, splits)
    ablation.to_csv("outputs/tables/ablation_study.csv", index=False)

    models, cm_res, cv_res = phase3_modeling.run_models(df, splits)
    models.to_csv("outputs/tables/model_evaluations.csv", index=False)
    cm_res.to_csv("outputs/tables/confusion_matrices.csv", index=False)
    cv_res.to_csv("outputs/tables/cross_validation.csv", index=False)

    sig = phase3_modeling.calculate_significance(preds_store)
    sig.to_csv("outputs/tables/significance_tests.csv", index=False)

    adv = phase4_adversarial.test_adversarial(df, splits)
    adv.to_csv("outputs/tables/adversarial_diagnostics.csv", index=False)

    phase5_sampling_viz.generate_sampling_artifacts(df, splits)
    phase5_sampling_viz.generate_ablation_chart(ablation)

    phase6_artifacts.generate_manifests()

    print("Pipeline complete.")

if __name__ == "__main__":
    run()
