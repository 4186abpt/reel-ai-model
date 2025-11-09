# reel-virality/config.py

import pathlib

# Define the absolute path to the project root directory
# This assumes the script is run from the project root or the script itself is near the root.
# Adjust .parent as necessary if config.py is placed deeper (e.g., if it was in src/)
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent

# --- Directories ---
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DIR = DATA_DIR / 'raw'
PROCESSED_DIR = DATA_DIR / 'processed'

# Raw Data Subdirectories (for the processing pipeline)
RAW_PENDING_DIR = RAW_DIR / 'pending'
RAW_COMPLETED_DIR = RAW_DIR / 'completed'

# Output Files
FEATURES_CSV = PROCESSED_DIR / 'features.csv'

# Ensure the necessary directories exist (important for the first run!)
for d in [RAW_PENDING_DIR, RAW_COMPLETED_DIR, PROCESSED_DIR]:
    d.mkdir(parents=True, exist_ok=True)

print(f"Project Root: {PROJECT_ROOT}")