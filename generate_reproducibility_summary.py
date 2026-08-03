import json
import pandas as pd
diff_size = len(open("outputs/reproducibility_diff.txt").read())
res = {"Pass": diff_size == 0, "Diff_Size_Bytes": diff_size}
pd.DataFrame([res]).to_csv("outputs/tables/reproducibility_diff_summary.csv", index=False)
