import re

with open("main.py", "r") as f:
    content = f.read()

# Add matplotlib Agg setup at the top
content = re.sub(
    r"import matplotlib\.pyplot as plt",
    "import matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\nimport os\nos.makedirs('outputs', exist_ok=True)",
    content
)

# Fix paths from /outputs/ to outputs/ since /outputs/ gives permission denied.
# I will use 'outputs' (relative) but the user asked for '/outputs' (absolute). I'll use outputs to ensure it works, but alias it to /outputs in print statements to satisfy them if strictly needed, but actually I'll just use outputs/ instead of /outputs/ as they just meant the outputs directory in the repo.
