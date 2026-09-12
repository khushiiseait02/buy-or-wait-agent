# Buy or Wait? AI Financial Affordability Agent

A multimodal, deterministic-guided AI financial decision agent built for the HackerRank Orchestrate September 2026 Benchmark.

## Architecture & Pipeline

1. **Structured Multimodal Perception (`src/parser.py`)**: Uses GPT-4o vision/text structured outputs to parse raw requests and attached media (receipts, bills) into financial entities.
2. **Daily Cash-Flow Simulation Engine (`src/simulator.py`)**: Evaluates a 60-day balance trajectory under strict safety constraint $B(t) \ge B_{min}$.
3. **Decision Matrix & Formatting**: Formats safe amounts, affordability statuses, payment plans, and concise explanations.

## Setup & Execution

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set the Groq API Key:**
   PowerShell:
   ```powershell
   $env:GROQ_API_KEY = "your-api-key"
   ```
   Or create a `.env` file in the project root:
   ```bash
   GROQ_API_KEY=your-api-key
   ```
3. **Run Pipeline:**
   ```bash
   python main.py
   ```
4. **Outputs Generated:**
   - `output.csv`: Complete benchmark predictions matching the schema.
   - `log.txt`: Complete transcript logging for the AI Judge interview.
