import urllib.request
import os

icons = {
    "db_gear_purple": "https://img.icons8.com/ios/96/8b5cf6/database.png",
    "table_gear_green": "https://img.icons8.com/ios/96/22c55e/table.png",
    "network_blue": "https://img.icons8.com/ios/96/3b82f6/network.png",
    "dashboard_orange": "https://img.icons8.com/ios/96/f97316/dashboard.png",
    "table_stars_purple": "https://img.icons8.com/ios/96/8b5cf6/grid.png",
    "gear_purple": "https://img.icons8.com/ios/96/8b5cf6/settings.png",
    "table_green": "https://img.icons8.com/ios/96/22c55e/grid.png",
    "sliders_green": "https://img.icons8.com/ios/96/22c55e/slider.png",
    "nodes_blue": "https://img.icons8.com/ios/96/3b82f6/nodes.png",
    "brain_blue": "https://img.icons8.com/ios/96/3b82f6/brain.png",
    "chart_orange": "https://img.icons8.com/ios/96/f97316/line-chart.png"
}

os.makedirs('icons', exist_ok=True)
for name, url in icons.items():
    try:
        urllib.request.urlretrieve(url, f'icons/{name}.png')
        print(f"Downloaded {name}")
    except Exception as e:
        print(f"Failed to download {name}: {e}")
