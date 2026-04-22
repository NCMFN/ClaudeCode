import re

with open("main.py", "r") as f:
    content = f.read()

# Make sure outputs/figures is created
content = content.replace("os.makedirs('outputs', exist_ok=True)", "os.makedirs('outputs/figures', exist_ok=True)")

# Fix CIRS distribution
content = content.replace("plt.savefig('outputs/cirs_class_distribution.png', dpi=150, bbox_inches='tight')", "plt.savefig('outputs/figures/cirs_class_distribution.png', dpi=300, bbox_inches='tight', facecolor='white')")
content = content.replace("print(\"Saved: outputs/cirs_class_distribution.png\")", "print('Saved: /outputs/figures/cirs_class_distribution.png')")

# Fix confusion matrix filenames
content = content.replace("'Logistic Regression': 'confusion_matrix_lr.png'", "'Logistic Regression': 'confusion_matrix_logreg.png'")
content = content.replace("'Random Forest': 'confusion_matrix_rf.png'", "'Random Forest': 'confusion_matrix_random_forest.png'")
content = content.replace("'XGBoost': 'confusion_matrix_xgb.png'", "'XGBoost': 'confusion_matrix_xgboost.png'")

# Fix confusion matrix save
content = content.replace("plt.savefig(f\"outputs/{cm_filenames[name]}\", dpi=150, bbox_inches='tight')", "plt.savefig(f\"outputs/figures/{cm_filenames[name]}\", dpi=300, bbox_inches='tight', facecolor='white')")
content = content.replace("print(f\"Saved: outputs/{cm_filenames[name]}\")", "print(f\"Saved: /outputs/figures/{cm_filenames[name]}\")")

# Fix Feature importance save
content = content.replace("plt.savefig(\"outputs/feature_importance.png\", dpi=150, bbox_inches='tight')", "plt.savefig('outputs/figures/feature_importance.png', dpi=300, bbox_inches='tight', facecolor='white')")
content = content.replace("print(\"Saved: outputs/feature_importance.png\")", "print('Saved: /outputs/figures/feature_importance.png')")

# Fix SHAP save
content = content.replace("plt.savefig(\"outputs/shap_summary.png\", dpi=150, bbox_inches='tight')", "plt.savefig('outputs/figures/shap_summary.png', dpi=300, bbox_inches='tight', facecolor='white')")
content = content.replace("print(\"Saved: outputs/shap_summary.png\")", "print('Saved: /outputs/figures/shap_summary.png')")

# Fix Sensitivity save
content = content.replace("plt.savefig('outputs/sensitivity_analysis.png', dpi=150, bbox_inches='tight')", "plt.savefig('outputs/figures/sensitivity_analysis_bar.png', dpi=300, bbox_inches='tight', facecolor='white')")
content = content.replace("print(\"Saved: outputs/sensitivity_analysis.png\")", "print('Saved: /outputs/figures/sensitivity_analysis_bar.png')")


# Update the final summary loop
import textwrap

summary_logic = textwrap.dedent("""
    import glob
    saved = glob.glob("outputs/figures/*.png")
    print("\\n=== SAVED FIGURES ===")
    for f in saved:
        print(f"/{f}")
""")

content = re.sub(
    r"print\(\"\\n=== FINAL FILES SAVED ===\"\)\s+for f in os\.listdir\('outputs'\):\s+print\(f\"  → outputs/\{f\}\"\)",
    summary_logic,
    content
)


with open("main.py", "w") as f:
    f.write(content)
