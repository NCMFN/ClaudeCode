import sys
import time

print("Starting test...")
sys.stdout.flush()
for i in range(3):
    print(f"Step {i}")
    sys.stdout.flush()
    time.sleep(1)
print("Done")
