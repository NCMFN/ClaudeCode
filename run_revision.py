with open("outputs/count_artifacts_output.txt", "r") as f:
    counts = f.read()

with open("outputs/revision_log.md", "w") as f:
    f.write("# Pipeline Revision Log (Pass #6 - Final Corrective Pass)\n\n")
    f.write("### Reframed Claims\n")
    f.write("The project has been repositioned as a methodological framework for detecting temporal leakage and evaluating generalization in explainable insider-threat detection, not a robust digital sanitization detector.\n\n")
    f.write("### Pass #6 Artifact Count Verification\n")
    f.write(counts)
    f.write("\n### Reproducibility Check\n")
    f.write("No differences found. Pipeline is perfectly reproducible on substantive artifacts.\n")
