import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

def generate_architecture():
    fig, ax = plt.subplots(figsize=(10, 14), dpi=400)
    ax.axis('off')

    # Define node positions (y goes from top to bottom)
    pos = {
        "VectAbundance Data": (3, 10),
        "ERA5-Land NetCDF": (7, 10),

        "Data Loader / Spatial Join": (5, 8.5),

        "Processed Merged Dataset": (5, 7.2),

        "Feature Engineering": (5, 5.9),

        "Climate Lags & Thermal\nAccumulation": (3, 4.4),
        "Spatial & Seasonality\nFeatures": (7, 4.4),

        "Model Training": (5, 2.9),

        "Random Forest Baseline": (2, 1.4),
        "XGBoost with Spatial CV": (5, 1.4),
        "LSTM 4-week Sliding\nWindow": (8, 1.4),

        "Model Evaluation": (5, 0),

        "SHAP Importance &\nResiduals": (3, -1.4),
        "Spatial-Temporal Forecast\nGrid": (7, -1.4),

        "GeoTIFF Raster Outputs": (5, -2.8),
        "Animated Seasonal GIF": (9, -2.8)
    }

    # Define explicit graph
    G = nx.DiGraph()
    edges = [
        ("VectAbundance Data", "Data Loader / Spatial Join"),
        ("ERA5-Land NetCDF", "Data Loader / Spatial Join"),

        ("Data Loader / Spatial Join", "Processed Merged Dataset"),

        ("Processed Merged Dataset", "Feature Engineering"),

        ("Feature Engineering", "Climate Lags & Thermal\nAccumulation"),
        ("Feature Engineering", "Spatial & Seasonality\nFeatures"),

        ("Climate Lags & Thermal\nAccumulation", "Model Training"),
        ("Spatial & Seasonality\nFeatures", "Model Training"),

        ("Model Training", "Random Forest Baseline"),
        ("Model Training", "XGBoost with Spatial CV"),
        ("Model Training", "LSTM 4-week Sliding\nWindow"),

        ("Random Forest Baseline", "Model Evaluation"),
        ("XGBoost with Spatial CV", "Model Evaluation"),
        ("LSTM 4-week Sliding\nWindow", "Model Evaluation"),

        ("Model Evaluation", "SHAP Importance &\nResiduals"),
        ("Model Evaluation", "Spatial-Temporal Forecast\nGrid"),

        ("Spatial-Temporal Forecast\nGrid", "GeoTIFF Raster Outputs"),
        ("Spatial-Temporal Forecast\nGrid", "Animated Seasonal GIF"),
    ]
    G.add_edges_from(edges)

    # Draw arrows manually for solid primary flow
    # Using a curve or straight line depending on the node positions
    for edge in G.edges():
        start = pos[edge[0]]
        end = pos[edge[1]]

        # Determine connection style based on node position to mimic the image
        if edge[0] == "Model Training" and edge[1] == "Random Forest Baseline":
            connectionstyle = "arc3,rad=0.2"
        elif edge[0] == "Model Training" and edge[1] == "LSTM 4-week Sliding\nWindow":
            connectionstyle = "arc3,rad=-0.2"
        elif edge[0] == "Random Forest Baseline" and edge[1] == "Model Evaluation":
            connectionstyle = "arc3,rad=-0.2"
        elif edge[0] == "LSTM 4-week Sliding\nWindow" and edge[1] == "Model Evaluation":
            connectionstyle = "arc3,rad=0.2"
        elif edge[0] == "Model Evaluation" and edge[1] == "SHAP Importance &\nResiduals":
            connectionstyle = "arc3,rad=0.2"
        elif edge[0] == "Model Evaluation" and edge[1] == "Spatial-Temporal Forecast\nGrid":
            connectionstyle = "arc3,rad=-0.2"
        elif edge[0] == "Spatial-Temporal Forecast\nGrid" and edge[1] == "GeoTIFF Raster Outputs":
            connectionstyle = "arc3,rad=0.2"
        elif edge[0] == "Spatial-Temporal Forecast\nGrid" and edge[1] == "Animated Seasonal GIF":
            connectionstyle = "arc3,rad=-0.2"
        elif edge[0] == "VectAbundance Data" and edge[1] == "Data Loader / Spatial Join":
             connectionstyle = "arc3,rad=0.2"
        elif edge[0] == "ERA5-Land NetCDF" and edge[1] == "Data Loader / Spatial Join":
             connectionstyle = "arc3,rad=-0.2"
        elif edge[0] == "Feature Engineering" and edge[1] == "Climate Lags & Thermal\nAccumulation":
             connectionstyle = "arc3,rad=0.2"
        elif edge[0] == "Feature Engineering" and edge[1] == "Spatial & Seasonality\nFeatures":
             connectionstyle = "arc3,rad=-0.2"
        elif edge[0] == "Climate Lags & Thermal\nAccumulation" and edge[1] == "Model Training":
             connectionstyle = "arc3,rad=-0.2"
        elif edge[0] == "Spatial & Seasonality\nFeatures" and edge[1] == "Model Training":
             connectionstyle = "arc3,rad=0.2"
        else:
            connectionstyle = "arc3,rad=0"

        ax.annotate("",
                    xy=end, xycoords='data',
                    xytext=start, textcoords='data',
                    arrowprops=dict(arrowstyle="->", color="gray", lw=1.5, shrinkA=30, shrinkB=30, connectionstyle=connectionstyle))

    # Draw Nodes as rounded rectangles (fancybox)
    for node, (x, y) in pos.items():
        color = "#EEF2FF"  # very light purple/blue

        box = mpatches.FancyBboxPatch((x - 1.4, y - 0.4), 2.8, 0.8,
                                      boxstyle="round,pad=0.1,rounding_size=0.2",
                                      ec="#D0D7F4", fc=color, lw=1.5)
        ax.add_patch(box)
        ax.text(x, y, node, ha="center", va="center", fontsize=11, fontweight='normal', zorder=10, color='black')

    plt.xlim(0, 10)
    plt.ylim(-4, 11)

    plt.savefig("system_architecture.png", bbox_inches='tight')
    print("Generated system_architecture.png")

if __name__ == "__main__":
    generate_architecture()
