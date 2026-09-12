import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
REQUESTS_CSV = DATASET_DIR / "requests.csv"
OUTPUT_CSV = BASE_DIR / "output.csv"
LOG_FILE = BASE_DIR / "log.txt"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
FORECAST_DAYS = 60
