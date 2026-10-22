import os
import glob
print("Figures:", len(glob.glob("outputs/figures/*.png")))
print("Tables:", len(glob.glob("outputs/tables/*.csv")))
