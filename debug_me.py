import sys
import os
import traceback

print("--- DEBUGGING START ---")
print(f"Current Directory: {os.getcwd()}")

# 1. Check if 'app' folder exists
if not os.path.exists("app"):
    print("CRITICAL ERROR: 'app' folder is missing!")
    sys.exit(1)

# 2. Check if 'main.py' is inside 'app'
if not os.path.exists("app/main.py"):
    print("CRITICAL ERROR: 'main.py' is NOT inside the 'app' folder.")
    print(f"Files found in 'app': {os.listdir('app')}")
    sys.exit(1)

# 3. Check for 'static' folder
if not os.path.exists("app/static"):
    print("WARNING: 'app/static' folder is missing. This might crash main.py.")
else:
    print("SUCCESS: Found 'app/static' folder.")

# 4. Try to import the app to see the REAL error
print("\nAttempting to import app.main...")
try:
    from app import main
    print("\nSUCCESS: app.main imported correctly! The issue might be with Uvicorn.")
except Exception as e:
    print("\n!!! IMPORT FAILED !!!")
    print("Here is the real error:")
    print("-" * 30)
    traceback.print_exc()  # This prints the specific line number that is crashing
    print("-" * 30)