import os
import sys

def main():
    figs = os.listdir('outputs/figures/')

    missing = []
    for i in range(1, 53):
        found = False
        for f in figs:
            if f.startswith(f"Figure_{i}_"):
                found = True
                size = os.path.getsize(os.path.join('outputs/figures', f))
                if size == 0:
                    print(f"Error: {f} exists but size is 0.")
                    sys.exit(1)
                break
        if not found:
            missing.append(i)

    if missing:
        print(f"Missing figures: {missing}")
        sys.exit(1)

    print("All 52 figures verified with non-zero size.")

if __name__ == "__main__":
    main()
