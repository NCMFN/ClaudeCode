with open("README.md", "r") as f:
    content = f.read()

content = content.replace("Enterprise Digital Sanitization Detection Pipeline", "Evaluation of ML Detection of Red-Team-Associated Sanitization Activity in Enterprise Authentication Telemetry")
content = content.replace("Research-grade ML pipeline that extends a prior small-scale insider-threat sanitization study into an enterprise-scale, adversarially-robust, explainable detection system.", "Research-grade methodological framework for detecting temporal leakage and evaluating generalization in explainable insider-threat detection. The central finding focuses on temporal shortcut learning, recontextualizing high performance as an artifact rather than true robustness.")

with open("README.md", "w") as f:
    f.write(content)
