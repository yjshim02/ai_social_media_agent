# AI Social Media Agent (Streamlit + FastAPI)

This project implements the hackathon spec:
- Brand inference (restricted to Super Bowl / Olympics context)
- Multi-variant post generation (caption + overlay + background image prompt + optional generated image)
- Agentic self-critique loop (2 iterations)
- Separate judge-scoring pass to rank variants (uses a second model call)
- Human-in-the-loop refinement (regenerate from selected variant)

## Quickstart (Mock mode — no API key needed)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt

# Terminal 1: backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2: frontend
streamlit run frontend/app.py
```

## OpenAI mode (when you get credits)
Set env vars:
```bash
# Windows PowerShell
setx AI_PROVIDER "openai"
setx OPENAI_API_KEY "YOUR_KEY"
setx OPENAI_TEXT_MODEL "gpt-5.2"
setx OPENAI_IMAGE_MODEL "gpt-image-1"

# macOS/Linux
export AI_PROVIDER=openai
export OPENAI_API_KEY="YOUR_KEY"
export OPENAI_TEXT_MODEL="gpt-5.2"
export OPENAI_IMAGE_MODEL="gpt-image-1"
```

Then run the same commands as above.

## API Endpoints
- POST /generate  -> returns 3 post variants (each improved by 2 critique loops)
- Each returned variant includes a `judge` block with 0-100 scores and rationale
- POST /refine    -> refines a selected variant given user feedback

## Notes
- The image layer supports:
  - mock: returns a simple placeholder SVG (so your demo always works)
  - openai: uses `client.images.generate(...)` and returns base64 PNG data
