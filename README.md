# Karma AI

A powerful multi-AI chat web app with **9 AI providers**, **76 built-in tools** (50 AI + 26 live data), **9 Indian languages**, voice input/output, image upload, chat history, and PWA support.

## Features

**9 AI Providers (all free tiers):**
- Sarvam (sarvam-105b), Gemini (gemini-3.6-flash), Groq (llama-3.3-70b), OpenRouter, Cerebras, Mistral, Cohere, HuggingFace, SambaNova

**9 Languages:**
- English, Hindi, Hinglish, Tamil, Telugu, Bengali, Marathi, Punjabi, Gujarati

**76 Tools:**
- 50 AI tools (Writing, Code, Language, Productivity, Education, Business, Creative, Utility)
- 26 live data tools (Weather, Wikipedia, Stock Market, Cricket, News, Movies, Currency, Dictionary, etc.)

**Extra features:**
- Chat history persistence (localStorage)
- Multiple chat sessions
- Markdown rendering
- Voice input (SpeechRecognition) + Voice output (speechSynthesis)
- Image upload with Gemini vision
- 100% SVG icons, dark theme, PWA installable

## Quick Start

```bash
pip install -r requirements.txt
python app.py
# Open http://localhost:5000
```

## Deploy to Render.com
1. Push to GitHub
2. render.com → New Web Service → select repo
3. Build: `pip install -r requirements.txt`
4. Start: `python app.py`
5. Add env vars: SARVAM_API_KEY, GEMINI_API_KEY

## Security
Never commit config.py. Use environment variables in production.
