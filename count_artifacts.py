import os
import glob

def main():
    figures = glob.glob('outputs/figures/*.png')
    tables = glob.glob('outputs/tables/*.csv')

    # Base numbers from prompt: 20 figures, 20 tables.
    base_figures = 20
    base_tables = 20

    net_new_figures = len(figures) - base_figures
    net_new_tables = len(tables) - base_tables

    print(f"Total Figures: {len(figures)}")
    print(f"Total Tables: {len(tables)}")
    print(f"Net-New Figures: {net_new_figures}")
    print(f"Net-New Tables: {net_new_tables}")

    print("\nItemized Figures:")
    for f in sorted([os.path.basename(p) for p in figures]):
        print(f" - {f}")

    print("\nItemized Tables:")
    for t in sorted([os.path.basename(p) for p in tables]):
        print(f" - {t}")

if __name__ == '__main__':
    main()
