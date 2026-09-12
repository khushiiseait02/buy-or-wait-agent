import pandas as pd
from pathlib import Path
from src.config import REQUESTS_CSV, OUTPUT_CSV, LOG_FILE, DATASET_DIR
from src.parser import parse_request_context
from src.simulator import run_affordability_simulation

def logger(log_fp, req_id: str, prompt: str, context_json: str, decision_json: str):
    log_fp.write(f"--- REQUEST ID: {req_id} ---\n")
    log_fp.write(f"[PROMPT]:\n{prompt}\n\n")
    log_fp.write(f"[EXTRACTED CONTEXT]:\n{context_json}\n\n")
    log_fp.write(f"[DECISION]:\n{decision_json}\n")
    log_fp.write("=" * 60 + "\n\n")

def main():
    if not REQUESTS_CSV.exists():
        print(f"Dataset file not found at {REQUESTS_CSV}. Please place requests.csv in dataset/")
        return

    df = pd.read_csv(REQUESTS_CSV)
    decisions = []

    with open(LOG_FILE, "w", encoding="utf-8") as log_fp:
        log_fp.write("=== FINANCIAL AGENT LOG TRANSCRIPT ===\n\n")

        for idx, row in df.iterrows():
            req_id = str(row.get("request_id", idx))
            prompt = str(row.get("prompt", ""))
            
            raw_media = str(row.get("media_paths", "")) if pd.notna(row.get("media_paths")) else ""
            media_files = [
                DATASET_DIR / p.strip() 
                for p in raw_media.split(";") 
                if p.strip()
            ]

            context = parse_request_context(prompt, media_files)
            decision = run_affordability_simulation(req_id, context)

            logger(
                log_fp, 
                req_id, 
                prompt, 
                context.model_dump_json(indent=2), 
                decision.model_dump_json(indent=2)
            )

            decisions.append(decision.to_csv_dict())

    out_df = pd.DataFrame(decisions)
    out_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Successfully processed {len(decisions)} requests. Results saved to {OUTPUT_CSV}.")

if __name__ == "__main__":
    main()
