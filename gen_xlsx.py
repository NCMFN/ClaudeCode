import pandas as pd
import os
os.makedirs("deliverables", exist_ok=True)
with pd.ExcelWriter('deliverables/all_tables.xlsx') as writer:
    for f in os.listdir("outputs/tables"):
        if f.endswith(".csv"):
            df = pd.read_csv(os.path.join("outputs/tables", f))
            df.to_excel(writer, sheet_name=f[:31], index=False)
