# CareerPilot AI

CareerPilot AI is a premium AI-powered resume and interview coaching platform built with Streamlit and Groq AI.

## Highlights
- Modern glassmorphism dashboard with a premium SaaS feel
- Resume upload and parsing for PDF, DOCX, and TXT
- AI resume scoring and improvement suggestions
- ATS compatibility analysis with keyword scoring
- Interview practice and answer evaluation
- Career roadmap, skill-gap analysis, resume rewriting, and LinkedIn suggestions

## Getting Started
1. Create and activate a Python environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Make sure your `.env` contains `GROQ_API_KEY` and `MODEL_NAME=llama-3.3-70b-versatile`.
4. Run the app: `streamlit run app.py`

## Environment Variables
- `GROQ_API_KEY` — your Groq API key
- `MODEL_NAME` — defaults to `llama-3.3-70b-versatile`

## Deployment
- Deploy on Streamlit Community Cloud, Render, Railway, or Hugging Face Spaces.
- Make sure your environment variables are configured in the hosting platform.
