import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300
})

fig, ax = plt.subplots(figsize=(14, 10))
ax.axis('off')

# Bounding box for Identity & Authentication Engine
identity_auth_engine = patches.FancyBboxPatch((6, 4.5), 5.5, 4, boxstyle="round,pad=0.2",
                                              edgecolor='gold', facecolor='#FFFFE0', alpha=0.5, zorder=0)
ax.add_patch(identity_auth_engine)
ax.text(8.75, 8.3, 'Identity & Authentication Engine (Oauth2 + JWT)', ha='center', va='center', fontsize=9)

# Bounding box for ML Threat Detection Engine
ml_threat_engine = patches.FancyBboxPatch((4.5, 1.5), 5, 4, boxstyle="round,pad=0.2",
                                          edgecolor='gold', facecolor='#FFFFE0', alpha=0.5, zorder=0)
ax.add_patch(ml_threat_engine)
ax.text(7, 5.3, 'Machine Learning Threat Detection Engine', ha='center', va='center', fontsize=9)

# Bounding box for Incident Response Logic
incident_response = patches.FancyBboxPatch((0, 1), 3.5, 3, boxstyle="round,pad=0.2",
                                           edgecolor='gold', facecolor='#FFFFE0', alpha=0.5, zorder=0)
ax.add_patch(incident_response)
ax.text(1.75, 3.8, 'Incident Response Logic', ha='center', va='center', fontsize=9)

# Bounding box for SIEM Integration & Observability Engine
siem_engine = patches.FancyBboxPatch((3.5, -0.5), 8, 1.2, boxstyle="round,pad=0.2",
                                     edgecolor='gold', facecolor='#FFFFE0', alpha=0.5, zorder=0)
ax.add_patch(siem_engine)
ax.text(7.5, 0.5, 'SIEM Integration & Observability Engine', ha='center', va='center', fontsize=9)


# Draw boxes and text for main components
def add_block(ax, text, xy, width=2, height=0.6, facecolor='#E6E6FA', edgecolor='gray', zorder=1):
    rect = patches.FancyBboxPatch(xy, width, height, boxstyle="round,pad=0.1",
                                  edgecolor=edgecolor, facecolor=facecolor, zorder=zorder)
    ax.add_patch(rect)
    ax.text(xy[0] + width/2, xy[1] + height/2, text, ha='center', va='center', fontsize=9, wrap=True)
    return (xy[0] + width/2, xy[1] + height/2)

def add_database(ax, text, xy, width=1.5, height=1, facecolor='#E6E6FA', zorder=1):
    # Just draw a simple cylinder-like shape
    rect = patches.Rectangle(xy, width, height, edgecolor='gray', facecolor=facecolor, zorder=zorder)
    ax.add_patch(rect)
    ellipse_top = patches.Ellipse((xy[0]+width/2, xy[1]+height), width, height*0.3, edgecolor='gray', facecolor=facecolor, zorder=zorder)
    ellipse_bottom = patches.Ellipse((xy[0]+width/2, xy[1]), width, height*0.3, edgecolor='gray', facecolor=facecolor, zorder=zorder)
    ax.add_patch(ellipse_top)
    ax.add_patch(ellipse_bottom)
    ax.text(xy[0] + width/2, xy[1] + height/2, text, ha='center', va='center', fontsize=9)
    return (xy[0] + width/2, xy[1] + height/2)

# Nodes
cisco_b2b_api = add_block(ax, "Cisco Ariel B2B API", (8, 9))
api_gateway = add_block(ax, "API Gateway", (8, 7.5))

auth_check = add_block(ax, "Authentication Check", (6.5, 6))
auth_verify = add_block(ax, "Authorization Verify", (9.5, 6))
rbac_abac = add_block(ax, "RBAC/ABAC Validation", (9.5, 5))
identity_provider = add_database(ax, "Identity Provider", (9.5, 4.8), height=0.5)

feature_extraction = add_block(ax, "Feature Extraction", (6, 4))
rf_anomaly_detection = add_block(ax, "Random Forest Anomaly\nDetection", (6, 2.5))

benign_traffic = add_block(ax, "BENIGN TRAFFIC\n200 OK", (5, 1.5))
threat_traffic = add_block(ax, "Threat Traffic", (7, 1.5))
anomaly_detected = add_block(ax, "Anomaly Detected", (8, 1.5))
malicious_drop = add_block(ax, "MALICIOUS\nDROP/NULL", (9.5, 1.5))

threat_logger = add_database(ax, "Threat Logger", (5.2, 0.6), height=0.5)

auto_block_ip = add_block(ax, "Auto Block IP (WAF)", (0.5, 2.5))
db_blacklist = add_database(ax, "Database", (1, 1), height=0.5)

app_performance = add_block(ax, "Application Performance\nMonitoring", (3.8, -0.3))
kibana_dash = add_block(ax, "Kibana Dashboard", (6, -0.3))
traffic_analysis = add_block(ax, "Traffic Flow/Log Analysis", (8.5, -0.3))


# Connectors (Arrows)
def add_arrow(ax, start, end, style="->", connectionstyle="arc3"):
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(arrowstyle=style, color='gray', connectionstyle=connectionstyle))

add_arrow(ax, cisco_b2b_api, api_gateway)
add_arrow(ax, api_gateway, auth_check, connectionstyle="arc3,rad=-0.2")
add_arrow(ax, api_gateway, auth_verify, connectionstyle="arc3,rad=0.2")

add_arrow(ax, auth_verify, rbac_abac)
add_arrow(ax, rbac_abac, identity_provider)

add_arrow(ax, auth_check, feature_extraction)
add_arrow(ax, auth_verify, feature_extraction) # Needs fixing to not intersect text

add_arrow(ax, feature_extraction, rf_anomaly_detection)
add_arrow(ax, rf_anomaly_detection, benign_traffic, connectionstyle="arc3,rad=0.1")
add_arrow(ax, rf_anomaly_detection, threat_traffic, connectionstyle="arc3,rad=-0.1")
add_arrow(ax, rf_anomaly_detection, anomaly_detected, connectionstyle="arc3,rad=-0.1")

add_arrow(ax, threat_traffic, malicious_drop)
add_arrow(ax, anomaly_detected, malicious_drop)

add_arrow(ax, benign_traffic, threat_logger)

add_arrow(ax, benign_traffic, auto_block_ip) # Actually looks like threat_logger goes to auto_block_ip
add_arrow(ax, auto_block_ip, db_blacklist)

add_arrow(ax, threat_logger, kibana_dash)
add_arrow(ax, malicious_drop, traffic_analysis)


plt.suptitle("End-to-End Validation Pipeline", y=0.08, fontsize=16, fontweight='bold')
plt.title("Fig. 3. End-to-end empirical validation pipeline for MLASF-B2B.", y=0.03, fontsize=12)

plt.tight_layout()
plt.savefig('reproduced_diagram.png')
print("Saved reproduced diagram")
