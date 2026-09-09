from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import pandas as pd
import os

def generate_report():
    os.makedirs("outputs/report", exist_ok=True)
    doc = SimpleDocTemplate("outputs/report/micro_pricing_policy_report.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = styles['Title']
    h1_style = styles['Heading1']
    h2_style = styles['Heading2']
    normal_style = styles['Normal']

    # Title
    story.append(Paragraph("Micro-Pricing Dynamics & Revenue Infrastructure", title_style))
    story.append(Paragraph("Algorithmic Replacement vs. Human Intervention on UK National Rail Routes", h2_style))
    story.append(Spacer(1, 12))

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary", h1_style))
    metrics = pd.read_csv('outputs/tables/model_comparison_metrics.csv')
    best_r2 = metrics[metrics['Model'] == 'Decision Tree']['R²'].values[0]
    exec_text = (f"This report evaluates whether Decision Tree Regressors can replace manual corporate pricing "
                 f"policy on UK National Rail routes. The best performing Decision Tree model achieved an R² "
                 f"of {best_r2:.2f}, indicating that algorithmic models can capture a significant portion of "
                 f"pricing variance. However, human intervention remains essential for disruption management "
                 f"and equity preservation.")
    story.append(Paragraph(exec_text, normal_style))
    story.append(Spacer(1, 12))

    # 2. Model Performance Summary
    story.append(Paragraph("2. Model Performance Summary", h1_style))

    table_data = [metrics.columns.tolist()] + metrics.values.tolist()
    for i in range(1, len(table_data)):
        for j in range(1, len(table_data[i])):
            if isinstance(table_data[i][j], float):
                table_data[i][j] = f"{table_data[i][j]:.3f}"

    t = Table(table_data)
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey),
                           ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                           ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                           ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                           ('BOTTOMPADDING', (0,0), (-1,0), 12),
                           ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                           ('GRID', (0,0), (-1,-1), 1, colors.black)]))
    story.append(t)
    story.append(Spacer(1, 12))

    if os.path.exists("outputs/figures/figure_34.png"):
        story.append(Image("outputs/figures/figure_34.png", width=400, height=300))
        story.append(Spacer(1, 12))

    # 3. Top Feature Drivers
    story.append(Paragraph("3. Top Feature Drivers", h1_style))
    story.append(Paragraph("The most critical drivers of price at the micro-transaction level were extracted using the feature importances of the best Decision Tree model. 'advance_booking_days' and 'hour_of_departure' consistently rank high.", normal_style))
    if os.path.exists("outputs/figures/figure_37.png"):
        story.append(Image("outputs/figures/figure_37.png", width=400, height=300))
        story.append(Spacer(1, 12))

    # 4. Anomaly Intervention Map
    story.append(Paragraph("4. Anomaly Intervention Map", h1_style))
    story.append(Paragraph("Disruption events (e.g., Signal Failures, Weather) trigger significant pricing anomalies where the model fails to predict appropriately, requiring human oversight.", normal_style))

    human_interv = pd.read_csv('outputs/tables/human_intervention_nodes.csv').head(5)
    human_data = [human_interv.columns.tolist()] + human_interv.values.tolist()
    for i in range(1, len(human_data)):
        human_data[i][1] = f"{human_data[i][1]:.3f}"
        human_data[i][3] = f"{human_data[i][3]:.2f}"

    t2 = Table(human_data)
    t2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.lightblue),
                           ('GRID', (0,0), (-1,-1), 1, colors.black)]))
    story.append(t2)
    story.append(Spacer(1, 12))

    # 5. Equity Risk Assessment
    story.append(Paragraph("5. Equity Risk Assessment", h1_style))
    story.append(Paragraph("Algorithmic models naturally seek to maximize revenue, which can inadvertently increase prices for vulnerable demographics. Policy recommends enforcing minimum discount floors to cap algorithmic recommendations for Senior and Disabled Railcard holders.", normal_style))

    equity = pd.read_csv('outputs/tables/equity_risk_routes.csv').head(5)
    if not equity.empty:
        equity_data = [equity.columns.tolist()] + equity.values.tolist()
        for i in range(1, len(equity_data)):
            equity_data[i][2] = f"{equity_data[i][2]:.2f}"
            equity_data[i][3] = f"{equity_data[i][3]:.2f}"
            equity_data[i][4] = f"{equity_data[i][4]:.2f}%"
        t3 = Table(equity_data)
        t3.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.lightcoral),
                               ('GRID', (0,0), (-1,-1), 1, colors.black)]))
        story.append(t3)
    story.append(Spacer(1, 12))

    # 6. Route Elasticity Summary
    story.append(Paragraph("6. Route Elasticity Summary", h1_style))
    story.append(Paragraph("High elasticity routes demonstrate volatile pricing behavior, making them prime candidates for algorithmic deployment. Low elasticity routes are stable and should maintain existing human governance.", normal_style))
    if os.path.exists("outputs/figures/figure_55.png"):
        story.append(Image("outputs/figures/figure_55.png", width=300, height=350))
    story.append(Spacer(1, 12))

    # 7. Limitations & Future Work
    story.append(Paragraph("7. Limitations & Future Work", h1_style))
    story.append(Paragraph("It is important to note that the dataset used for this analysis is a mock/synthetic proxy (Maven Analytics) simulating real National Rail patterns. Future production deployment would require direct integration with the LENNON transaction feed under ATOC/RDG data-sharing agreements.", normal_style))

    doc.build(story)
    print("Report generated successfully.")

if __name__ == '__main__':
    generate_report()
