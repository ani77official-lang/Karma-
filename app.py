"""
Multi-AI Chat + Tools App v3
Supports: Sarvam, Gemini, Groq, OpenRouter, Cerebras, Mistral, Cohere, HuggingFace, SambaNova
Features: 9 languages, 70 tools (50 AI + 20 live), chat history, image upload, voice I/O
Run: python app.py  (then open http://localhost:5000)
"""
import os
import re
import json
import datetime
import base64
from urllib.parse import quote

import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="static", static_url_path="")

# --- API key handling ------------------------------------------------------
def _get_key(name):
    val = os.environ.get(name, "")
    if val:
        return val
    try:
        import config
        return getattr(config, name, "")
    except (ImportError, AttributeError):
        return ""

KEYS = {name: _get_key(name) for name in [
    "SARVAM_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY",
    "CEREBRAS_API_KEY", "MISTRAL_API_KEY", "COHERE_API_KEY", "HF_API_KEY", "SAMBANOVA_API_KEY",
]}

# --- Provider definitions --------------------------------------------------
PROVIDERS = {
    "sarvam": {"type":"openai","url":"https://api.sarvam.ai/v1/chat/completions","key_header":"api-subscription-key","model":"sarvam-105b","key_env":"SARVAM_API_KEY","label":"Sarvam","desc":"sarvam-105b · Best for Indian languages"},
    "gemini": {"type":"gemini","url":"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent","key_header":"x-goog-api-key","model":"gemini-3.6-flash","key_env":"GEMINI_API_KEY","label":"Gemini","desc":"gemini-3.6-flash · Google's fast model + vision"},
    "groq": {"type":"openai","url":"https://api.groq.com/openai/v1/chat/completions","key_header":"Authorization","key_prefix":"Bearer ","model":"llama-3.3-70b-versatile","key_env":"GROQ_API_KEY","label":"Groq","desc":"llama-3.3-70b · Ultra-fast"},
    "openrouter": {"type":"openai","url":"https://openrouter.ai/api/v1/chat/completions","key_header":"Authorization","key_prefix":"Bearer ","model":"meta-llama/llama-3.3-70b-instruct:free","key_env":"OPENROUTER_API_KEY","label":"OpenRouter","desc":"llama-3.3-70b · Free tier"},
    "cerebras": {"type":"openai","url":"https://api.cerebras.ai/v1/chat/completions","key_header":"Authorization","key_prefix":"Bearer ","model":"llama-3.3-70b","key_env":"CEREBRAS_API_KEY","label":"Cerebras","desc":"llama-3.3-70b · Wafer-scale"},
    "mistral": {"type":"openai","url":"https://api.mistral.ai/v1/chat/completions","key_header":"Authorization","key_prefix":"Bearer ","model":"mistral-small-latest","key_env":"MISTRAL_API_KEY","label":"Mistral","desc":"mistral-small · European AI"},
    "cohere": {"type":"cohere","url":"https://api.cohere.ai/v2/chat","key_header":"Authorization","key_prefix":"Bearer ","model":"command-r-plus","key_env":"COHERE_API_KEY","label":"Cohere","desc":"command-r-plus · RAG"},
    "huggingface": {"type":"openai","url":"https://api-inference.huggingface.co/models/meta-llama/Llama-3.3-70B-Instruct/v1/chat/completions","key_header":"Authorization","key_prefix":"Bearer ","model":"meta-llama/Llama-3.3-70B-Instruct","key_env":"HF_API_KEY","label":"HuggingFace","desc":"Llama-3.3-70B"},
    "sambanova": {"type":"openai","url":"https://api.sambanova.ai/v1/chat/completions","key_header":"Authorization","key_prefix":"Bearer ","model":"Meta-Llama-3.3-70B-Instruct","key_env":"SAMBANOVA_API_KEY","label":"SambaNova","desc":"Llama-3.3-70B"},
}

# --- System prompts per language (9 languages) -----------------------------
LANG_PROMPTS = {
    "english": "You are a friendly, helpful AI assistant. Answer clearly and concisely. Always respond in English. Use Markdown formatting (bold, lists, code blocks) for better readability.",
    "hindi": "You are a friendly, helpful AI assistant. Answer clearly and concisely. Always respond in Hindi using Devanagari script (हिंदी). Use Markdown formatting for better readability.",
    "hinglish": "You are a friendly, helpful AI assistant. Answer clearly and concisely. Always respond in Hinglish — Hindi written in Roman/English letters (like 'aap kaise ho?'). Never use Devanagari script. Use Markdown formatting.",
    "tamil": "You are a friendly, helpful AI assistant. Answer clearly and concisely. Always respond in Tamil (தமிழ்). Use Markdown formatting for better readability.",
    "telugu": "You are a friendly, helpful AI assistant. Answer clearly and concisely. Always respond in Telugu (తెలుగు). Use Markdown formatting for better readability.",
    "bengali": "You are a friendly, helpful AI assistant. Answer clearly and concisely. Always respond in Bengali (বাংলা). Use Markdown formatting for better readability.",
    "marathi": "You are a friendly, helpful AI assistant. Answer clearly and concisely. Always respond in Marathi (मराठी). Use Markdown formatting for better readability.",
    "punjabi": "You are a friendly, helpful AI assistant. Answer clearly and concisely. Always respond in Punjabi (ਪੰਜਾਬੀ). Use Markdown formatting for better readability.",
    "gujarati": "You are a friendly, helpful AI assistant. Answer clearly and concisely. Always respond in Gujarati (ગુજરાતી). Use Markdown formatting for better readability.",
}


# --- API call implementations ----------------------------------------------
def call_openai_compatible(url, key_header, key_prefix, api_key, model, messages, system_prompt, temperature):
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    payload = {"model": model, "messages": full_messages, "temperature": temperature}
    headers = {"Content-Type": "application/json"}
    headers[key_header] = (key_prefix or "") + api_key
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def call_gemini(url, api_key, messages, system_prompt, temperature, image_data=None):
    contents = []
    for m in messages:
        role = "model" if m["role"] == "assistant" else "user"
        if m.get("image"):
            # Vision: include inline image + text
            parts = []
            if m.get("content"):
                parts.append({"text": m["content"]})
            parts.append({"inlineData": {"mimeType": m.get("image_mime", "image/jpeg"), "data": m["image"]}})
            contents.append({"role": role, "parts": parts})
        else:
            contents.append({"role": role, "parts": [{"text": m["content"]}]})
    payload = {"contents": contents, "systemInstruction": {"parts": [{"text": system_prompt}]}, "generationConfig": {"temperature": temperature}}
    resp = requests.post(url, headers={"x-goog-api-key": api_key, "Content-Type": "application/json"}, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError(data.get("promptFeedback", {}).get("blockReason", "No candidates returned"))
    parts = candidates[0].get("content", {}).get("parts", [])
    return "".join(p.get("text", "") for p in parts) or "(empty response)"

def call_cohere(url, api_key, model, messages, system_prompt, temperature):
    cohere_messages = [{"role": "system", "content": system_prompt}]
    for m in messages:
        cohere_messages.append({"role": m["role"], "content": m["content"]})
    payload = {"model": model, "messages": cohere_messages, "temperature": temperature}
    resp = requests.post(url, headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    if "message" in data:
        content = data["message"].get("content", [])
        return "".join(p.get("text", "") for p in content) if isinstance(content, list) else content
    raise RuntimeError("Unexpected Cohere response")

def dispatch(provider_id, messages, system_prompt, temperature):
    p = PROVIDERS[provider_id]
    api_key = KEYS.get(p["key_env"], "")
    if not api_key:
        raise ValueError(f"API key for {p['label']} is not configured. Set {p['key_env']} env var or edit config.py.")
    if p["type"] == "openai":
        return call_openai_compatible(p["url"], p["key_header"], p.get("key_prefix",""), api_key, p["model"], messages, system_prompt, temperature)
    elif p["type"] == "gemini":
        return call_gemini(p["url"], api_key, messages, system_prompt, temperature)
    elif p["type"] == "cohere":
        return call_cohere(p["url"], api_key, p["model"], messages, system_prompt, temperature)
    raise ValueError(f"Unknown provider type: {p['type']}")


# --- Routes: Chat + Tool + Image --------------------------------------------
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/providers")
def providers():
    return jsonify({pid: {"label":p["label"],"desc":p["desc"],"model":p["model"],"configured":bool(KEYS.get(p["key_env"],""))} for pid,p in PROVIDERS.items()})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])
    provider = data.get("provider", "sarvam")
    language = data.get("language", "english")
    temperature = data.get("temperature", 0.7)
    system_override = data.get("system_prompt")
    if not messages:
        return jsonify({"error": "No messages provided."}), 400
    if provider not in PROVIDERS:
        return jsonify({"error": f"Unknown provider: {provider}"}), 400
    system_prompt = system_override if system_override else LANG_PROMPTS.get(language, LANG_PROMPTS["english"])
    # Handle image upload (Gemini vision only for now)
    if data.get("image") and provider == "gemini":
        # Attach image to the last user message
        if messages:
            messages[-1]["image"] = data["image"]
            messages[-1]["image_mime"] = data.get("image_mime", "image/jpeg")
    try:
        reply = dispatch(provider, messages, system_prompt, temperature)
        return jsonify({"reply": reply, "provider": provider})
    except requests.exceptions.HTTPError as e:
        body = e.response.text[:500] if e.response is not None else ""
        status = e.response.status_code if e.response is not None else 500
        return jsonify({"error": f"{PROVIDERS[provider]['label']} API error ({status}): {body}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/tool", methods=["POST"])
def tool():
    data = request.get_json(silent=True) or {}
    provider = data.get("provider", "sarvam")
    language = data.get("language", "english")
    tool_prompt = data.get("prompt", "")
    tool_input = data.get("input", "")
    if not tool_prompt:
        return jsonify({"error": "No tool prompt provided."}), 400
    if provider not in PROVIDERS:
        return jsonify({"error": f"Unknown provider: {provider}"}), 400
    system_prompt = LANG_PROMPTS.get(language, LANG_PROMPTS["english"]) + "\n\n" + tool_prompt
    messages = [{"role": "user", "content": tool_input}] if tool_input else [{"role": "user", "content": "Please generate the output."}]
    try:
        reply = dispatch(provider, messages, system_prompt, data.get("temperature", 0.7))
        return jsonify({"reply": reply, "provider": provider})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Live data tools (no API key needed) -----------------------------------
def _safe_get(url, **kwargs):
    resp = requests.get(url, timeout=15, **kwargs)
    resp.raise_for_status()
    return resp.json()

@app.route("/api/live", methods=["POST"])
def live_tool():
    data = request.get_json(silent=True) or {}
    action = data.get("action", "")
    inp = (data.get("input", "") or "").strip()
    try:
        # --- Current Time ---
        if action == "time":
            tz = inp if inp else "Asia/Kolkata"
            try:
                tdata = _safe_get(f"https://timeapi.io/api/Time/current/zone?timeZone={quote(tz)}")
                time_str = f"{tdata.get('dateTime', 'Unknown')}\nTimezone: {tdata.get('timeZone', tz)}"
                if 'dayOfWeek' in tdata: time_str += f"\nDay: {tdata['dayOfWeek']}"
                return jsonify({"reply": time_str})
            except Exception:
                now = datetime.datetime.now(datetime.timezone.utc)
                return jsonify({"reply": f"Current time (UTC): {now.strftime('%Y-%m-%d %H:%M:%S')}\n(Note: Could not fetch for timezone '{tz}', showing UTC.)"})

        # --- Wikipedia ---
        elif action == "wikipedia":
            if not inp: return jsonify({"error": "Enter a search term."}), 400
            sdata = _safe_get(f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote(inp)}&format=json&srlimit=1")
            results = sdata.get("query", {}).get("search", [])
            if not results: return jsonify({"reply": f"No Wikipedia articles found for '{inp}'."})
            title = results[0]["title"]
            sdata2 = _safe_get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title)}")
            reply = f"**{sdata2.get('title', title)}**\n\n{sdata2.get('extract', 'No summary available.')}\n\nRead more: {sdata2.get('content_urls', {}).get('desktop', {}).get('page', '')}"
            return jsonify({"reply": reply})

        # --- Weather (Open-Meteo) ---
        elif action == "weather":
            if not inp: return jsonify({"error": "Enter a city name."}), 400
            gdata = _safe_get(f"https://geocoding-api.open-meteo.com/v1/search?name={quote(inp)}&count=1&format=json")
            locs = gdata.get("results", [])
            if not locs: return jsonify({"reply": f"Could not find city '{inp}'."})
            loc = locs[0]; lat, lon = loc["latitude"], loc["longitude"]
            wdata = _safe_get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,weather_code&timezone=auto&forecast_days=3")
            c = wdata.get("current", {}); d = wdata.get("daily", {})
            wmo = {0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",45:"Foggy",48:"Rime fog",51:"Light drizzle",53:"Drizzle",55:"Heavy drizzle",61:"Light rain",63:"Rain",65:"Heavy rain",71:"Light snow",73:"Snow",75:"Heavy snow",80:"Rain showers",81:"Showers",82:"Heavy showers",95:"Thunderstorm",96:"Thunderstorm+hail",99:"Heavy thunderstorm+hail"}
            cond = wmo.get(c.get("weather_code", 0), "Unknown")
            reply = f"**Weather for {loc['name']}, {loc.get('country','')}**\n\nCurrent: {cond}\nTemperature: {c.get('temperature_2m','?')}°C (feels like {c.get('apparent_temperature','?')}°C)\nHumidity: {c.get('relative_humidity_2m','?')}%\nWind: {c.get('wind_speed_10m','?')} km/h\n\n**3-Day Forecast:**\n"
            if d:
                for i in range(min(3, len(d.get("time", [])))):
                    reply += f"  {d['time'][i]}: {wmo.get(d['weather_code'][i],'?')}, {d['temperature_2m_min'][i]}°C - {d['temperature_2m_max'][i]}°C\n"
            return jsonify({"reply": reply})

        # --- Dictionary ---
        elif action == "dictionary":
            if not inp: return jsonify({"error": "Enter a word."}), 400
            try: ddata = _safe_get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote(inp)}")
            except requests.exceptions.HTTPError: return jsonify({"reply": f"No dictionary entry found for '{inp}'."})
            reply = f"**{inp.upper()}**\n\n"
            for entry in ddata[:2]:
                for meaning in entry.get("meanings", [])[:3]:
                    reply += f"*{meaning.get('partOfSpeech','')}*\n"
                    for defn in meaning.get("definitions", [])[:3]:
                        reply += f"  - {defn.get('definition','')}\n"
                        if defn.get("example"): reply += f"    Example: \"{defn['example']}\"\n"
                    reply += "\n"
            return jsonify({"reply": reply})

        # --- Currency ---
        elif action == "currency":
            if not inp: return jsonify({"error": "Enter like: 100 USD to INR"}), 400
            m = re.match(r"([\d,.]+)\s*([A-Za-z]{3})\s*(?:to|in)\s*([A-Za-z]{3})", inp)
            if not m: return jsonify({"error": "Format: '100 USD to INR'"}), 400
            amount = float(m.group(1).replace(",", "")); base = m.group(2).lower(); target = m.group(3).lower()
            try: cdata = _safe_get(f"https://cdn.jsdelivr.net/gh/NemesisX1/currency-api@main/v1/currencies/{base}.json")
            except requests.exceptions.HTTPError: return jsonify({"reply": f"Could not find rates for {base.upper()}."})
            rate = cdata.get(base, {}).get(target)
            if not rate: return jsonify({"reply": f"Could not find rate for {base.upper()} to {target.upper()}."})
            reply = f"**Currency Conversion**\n\n{amount:,.2f} {base.upper()} = {amount * rate:,.2f} {target.upper()}\nRate: 1 {base.upper()} = {rate:.4f} {target.upper()}\nDate: {cdata.get('date','unknown')}"
            return jsonify({"reply": reply})

        # --- Number Fact ---
        elif action == "number_fact":
            if not inp: return jsonify({"reply": "Enter a number, or 'random'."})
            url = "https://numbersapi.com/random/trivia?json" if inp.lower() == "random" else f"https://numbersapi.com/{quote(inp)}/trivia?json"
            try: return jsonify({"reply": _safe_get(url).get("text", "No fact found.")})
            except Exception: return jsonify({"reply": f"Could not fetch fact for '{inp}'."})

        # --- Quote ---
        elif action == "quote":
            try:
                qdata = _safe_get("https://api.quotable.io/random")
                return jsonify({"reply": f"\"{qdata.get('content','')}\"\n— {qdata.get('author','')}"})
            except Exception:
                import random
                qs = [("The only way to do great work is to love what you do.","Steve Jobs"),("Be the change you wish to see in the world.","Mahatma Gandhi")]
                q,a = random.choice(qs); return jsonify({"reply": f"\"{q}\"\n— {a}"})

        # --- Joke ---
        elif action == "joke":
            try:
                jdata = _safe_get("https://official-joke-api.appspot.com/random_joke")
                return jsonify({"reply": f"{jdata.get('setup','')}\n\n{jdata.get('punchline','')}"})
            except Exception: return jsonify({"reply": "Why don't programmers like nature? It has too many bugs."})

        # --- IP Info ---
        elif action == "ip_info":
            try:
                idata = _safe_get("https://ipapi.co/json/")
                reply = f"**IP Information**\n\nIP: {idata.get('ip','?')}\nCity: {idata.get('city','?')}\nRegion: {idata.get('region','?')}\nCountry: {idata.get('country_name','?')} ({idata.get('country','?')})\nISP: {idata.get('org','?')}\nTimezone: {idata.get('timezone','?')}"
                return jsonify({"reply": reply})
            except Exception: return jsonify({"reply": "Could not fetch IP information."})

        # --- Hacker News ---
        elif action == "hackernews":
            try:
                ids = _safe_get("https://hacker-news.firebaseio.com/v0/topstories.json")
                reply = "**Top 5 Hacker News Stories**\n\n"
                for sid in ids[:5]:
                    story = _safe_get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
                    reply += f"- {story.get('title','?')} ({story.get('score',0)} points)\n  {story.get('url','')}\n"
                return jsonify({"reply": reply})
            except Exception: return jsonify({"reply": "Could not fetch Hacker News stories."})

        # --- Country Info ---
        elif action == "country":
            if not inp: return jsonify({"error": "Enter a country name."}), 400
            try:
                cdata = _safe_get(f"https://restcountries.com/v3.1/name/{quote(inp)}?fields=name,capital,population,region,languages,currencies,flag")
                c = cdata[0]; name = c.get("name",{}).get("common",inp)
                reply = f"**{name}** {c.get('flag','')}\n\nCapital: {', '.join(c.get('capital',['?']))}\nPopulation: {c.get('population',0):,}\nRegion: {c.get('region','?')}\nLanguages: {', '.join(c.get('languages',{}).values())}"
                return jsonify({"reply": reply})
            except Exception: return jsonify({"reply": f"Could not find country '{inp}'."})

        # --- NASA ---
        elif action == "space":
            try:
                sdata = _safe_get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY")
                reply = f"**Astronomy Picture of the Day**\n\n**{sdata.get('title','')}**\n\n{sdata.get('explanation','')}\n\nImage: {sdata.get('url','')}"
                return jsonify({"reply": reply})
            except Exception: return jsonify({"reply": "Could not fetch NASA data."})

        # --- GitHub ---
        elif action == "github":
            if not inp: return jsonify({"error": "Enter a GitHub username."}), 400
            try:
                udata = _safe_get(f"https://api.github.com/users/{quote(inp)}")
                reply = f"**GitHub: {udata.get('name', inp)}**\n\nUsername: @{udata.get('login','?')}\nBio: {udata.get('bio','None')}\nPublic Repos: {udata.get('public_repos',0)}\nFollowers: {udata.get('followers',0)} | Following: {udata.get('following',0)}\nProfile: {udata.get('html_url','')}"
                return jsonify({"reply": reply})
            except Exception: return jsonify({"reply": f"Could not find GitHub user '{inp}'."})

        # --- Advice ---
        elif action == "advice":
            try:
                adata = _safe_get("https://api.adviceslip.com/advice")
                return jsonify({"reply": f"Advice #{adata.get('slip',{}).get('id','')}: {adata.get('slip',{}).get('advice','')}"})
            except Exception: return jsonify({"reply": "Take it easy and keep going."})

        # --- Dog ---
        elif action == "dog":
            try:
                ddata = _safe_get("https://dog.ceo/api/breeds/image/random")
                return jsonify({"reply": f"Random Dog Photo:\n{ddata.get('message','')}"})
            except Exception: return jsonify({"reply": "Could not fetch dog photo."})

        # --- Cat Fact ---
        elif action == "cat_fact":
            try: return jsonify({"reply": _safe_get("https://catfact.ninja/fact").get("fact", "Cats are awesome.")})
            except Exception: return jsonify({"reply": "Cats sleep for 70% of their lives."})

        # --- Trivia ---
        elif action == "trivia":
            try:
                tdata = _safe_get("https://opentdb.com/api.php?amount=1&type=multiple")
                q = tdata.get("results", [{}])[0]
                import html as H, random as R
                question = H.unescape(q.get("question","")); correct = H.unescape(q.get("correct_answer",""))
                options = [H.unescape(o) for o in q.get("incorrect_answers",[])] + [correct]; R.shuffle(options)
                reply = f"**Trivia Question**\n\nCategory: {q.get('category','?')}\nDifficulty: {q.get('difficulty','?')}\n\n{question}\n\n"
                for i, opt in enumerate(options): reply += f"  {chr(65+i)}) {opt}\n"
                reply += f"\n(Answer: {correct})"
                return jsonify({"reply": reply})
            except Exception: return jsonify({"reply": "Could not fetch trivia."})

        # --- Sunrise/Sunset ---
        elif action == "sunrise":
            if not inp: return jsonify({"error": "Enter a city name."}), 400
            try:
                gdata = _safe_get(f"https://geocoding-api.open-meteo.com/v1/search?name={quote(inp)}&count=1&format=json")
                loc = gdata["results"][0]; lat, lon = loc["latitude"], loc["longitude"]
                sdata = _safe_get(f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=0")
                r = sdata.get("results", {})
                reply = f"**Sun Times for {loc['name']}, {loc.get('country','')}**\n\nSunrise: {r.get('sunrise','?')}\nSunset: {r.get('sunset','?')}\nSolar Noon: {r.get('solar_noon','?')}\nDay Length: {r.get('day_length','?')} seconds"
                return jsonify({"reply": reply})
            except Exception: return jsonify({"reply": f"Could not fetch sun times for '{inp}'."})

        # --- HTTP Status ---
        elif action == "http_status":
            if not inp: return jsonify({"error": "Enter an HTTP status code."}), 400
            try:
                hdata = _safe_get(f"https://httpstat.us/{quote(inp)}")
                return jsonify({"reply": f"HTTP {hdata.get('code','?')}: {hdata.get('description','?')}"})
            except Exception: return jsonify({"reply": f"Could not look up HTTP status {inp}."})

        # --- QR Code ---
        elif action == "qr_code":
            if not inp: return jsonify({"error": "Enter text or URL."}), 400
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={quote(inp)}"
            return jsonify({"reply": f"QR Code for: {inp}\n\nOpen this URL to view/download:\n{qr_url}"})

        # ===== NEW LIVE TOOLS (71-76) =====

        # --- Stock Market (Yahoo Finance, no key) ---
        elif action == "stock":
            if not inp: return jsonify({"error": "Enter a stock symbol, e.g. 'RELIANCE' or 'TCS' or 'INFY'"}), 400
            symbol = inp.upper().strip()
            if "." not in symbol: symbol += ".NS"  # Default NSE
            try:
                sdata = _safe_get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d",
                                  headers={"User-Agent": "Mozilla/5.0"})
                meta = sdata.get("chart", {}).get("result", [{}])[0].get("meta", {})
                price = meta.get("regularMarketPrice", 0)
                prev = meta.get("chartPreviousClose", 0)
                change = price - prev
                pct = (change / prev * 100) if prev else 0
                sign = "+" if change >= 0 else ""
                currency = meta.get("currency", "INR")
                reply = f"**{meta.get('symbol', symbol)}**\n\n"
                reply += f"Current Price: {currency} {price:,.2f}\n"
                reply += f"Change: {sign}{change:,.2f} ({sign}{pct:.2f}%)\n"
                reply += f"Previous Close: {currency} {prev:,.2f}\n"
                reply += f"Exchange: {meta.get('exchangeName', '?')}\n"
                reply += f"Currency: {currency}"
                return jsonify({"reply": reply})
            except Exception: return jsonify({"reply": f"Could not fetch stock data for '{inp}'. Try symbols like RELIANCE, TCS, INFY, HDFCBANK."})

        # --- Cricket Scores (SportScore, no key) ---
        elif action == "cricket":
            try:
                cdata = _safe_get("https://sportscore.com/api/widget/matches/?sport=cricket&limit=10",
                                   headers={"User-Agent": "Mozilla/5.0"})
                matches = cdata.get("matches", [])
                if not matches: return jsonify({"reply": "No cricket matches found right now."})
                reply = "**Live & Recent Cricket Matches**\n\n"
                for m in matches[:10]:
                    status = m.get("status", "?")
                    home = m.get("home_team", {}).get("name", "?")
                    away = m.get("away_team", {}).get("name", "?")
                    scores = m.get("scores", "")
                    reply += f"- **{home} vs {away}**\n"
                    if scores: reply += f"  Score: {scores}\n"
                    reply += f"  Status: {status}\n"
                return jsonify({"reply": reply})
            except Exception: return jsonify({"reply": "Could not fetch cricket scores."})

        # --- News Headlines (RSS via Google News) ---
        elif action == "news":
            try:
                import xml.etree.ElementTree as ET
                topic = inp if inp else "India"
                resp = requests.get(f"https://news.google.com/rss/search?q={quote(topic)}&hl=en-IN&gl=IN&ceid=IN:en", timeout=15,
                                     headers={"User-Agent": "Mozilla/5.0"})
                resp.raise_for_status()
                root = ET.fromstring(resp.content)
                items = root.findall(".//item")[:8]
                reply = f"**Top News: {topic}**\n\n"
                for i, item in enumerate(items, 1):
                    title = item.findtext("title", "").split(" - ")[0]
                    link = item.findtext("link", "")
                    reply += f"{i}. {title}\n"
                return jsonify({"reply": reply})
            except Exception: return jsonify({"reply": f"Could not fetch news for '{topic}'."})

        # --- Movie/TV/Anime Info (TVMaze API, no key) ---
        elif action == "movies":
            if not inp: return jsonify({"error": "Enter a movie or TV show name, e.g. 'Breaking Bad' or 'Inception'"}), 400
            try:
                mdata = _safe_get(f"https://api.tvmaze.com/singlesearch/shows?q={quote(inp)}&embed=cast")
                name = mdata.get("name", inp)
                premiered = mdata.get("premiered", "?")
                rating = mdata.get("rating", {}).get("average", "?")
                summary = re.sub("<[^>]+>", "", mdata.get("summary", "No summary available."))
                genres = ", ".join(mdata.get("genres", []))
                network = mdata.get("network", {}) or mdata.get("webChannel", {})
                reply = f"**{name}**\n\n"
                if genres: reply += f"Genres: {genres}\n"
                reply += f"Premiered: {premiered}\n"
                reply += f"Rating: {rating}/10\n"
                if network: reply += f"Network: {network.get('name','?')}\n"
                reply += f"\n{summary[:500]}\n"
                cast_data = mdata.get("_embedded", {}).get("cast", [])
                if cast_data:
                    reply += "\n**Cast:**\n"
                    for c in cast_data[:5]:
                        person = c.get("person", {}).get("name", "?")
                        char = c.get("character", {}).get("name", "?")
                        reply += f"  {person} as {char}\n"
                return jsonify({"reply": reply})
            except Exception: return jsonify({"reply": f"Could not find '{inp}'."})

        # --- YouTube Search (generates search URL, no key) ---
        elif action == "youtube":
            if not inp: return jsonify({"error": "Enter a search term for YouTube."}), 400
            search_url = f"https://www.youtube.com/results?search_query={quote(inp)}"
            reply = f"**YouTube Search: {inp}**\n\nOpen this link to see results:\n{search_url}\n\nOr search directly on YouTube for: {inp}"
            return jsonify({"reply": reply})

        # --- Unit Converter (pure Python, no API) ---
        elif action == "unit_converter":
            if not inp: return jsonify({"error": "Enter like: '5 kg to lbs' or '30 C to F' or '1 km to miles'"}), 400
            units = {
                "kg":("weight",1), "g":("weight",0.001), "lb":("weight",0.453592), "lbs":("weight",0.453592),
                "km":("length",1000), "m":("length",1), "cm":("length",0.01), "mm":("length",0.001),
                "mile":("length",1609.34), "miles":("length",1609.34), "ft":("length",0.3048), "feet":("length",0.3048),
                "inch":("length",0.0254), "inches":("length",0.0254), "yard":("length",0.9144),
                "l":("volume",1), "liter":("volume",1), "litre":("volume",1), "ml":("volume",0.001),
                "gallon":("volume",3.78541), "gal":("volume",3.78541),
                "c":("temp","c"), "celsius":("temp","c"), "f":("temp","f"), "fahrenheit":("temp","f"),
                "k":("temp","k"), "kelvin":("temp","k"),
                "hour":("time",3600), "hr":("time",3600), "h":("time",3600), "min":("time",60), "minute":("time",60),
                "sec":("time",1), "second":("time",1), "day":("time",86400),
                "mph":("speed",0.44704), "kmh":("speed",0.277778), "km/h":("speed",0.277778), "m/s":("speed",1),
            }
            m = re.match(r"([\d.]+)\s*(\w+)\s*(?:to|in)\s*(\w+)", inp, re.IGNORECASE)
            if not m: return jsonify({"error": "Format: '5 kg to lbs' or '30 C to F'"}), 400
            val = float(m.group(1)); from_u = m.group(2).lower(); to_u = m.group(3).lower()
            if from_u not in units or to_u not in units:
                return jsonify({"reply": f"Unknown unit. Supported: kg, g, lb, km, m, cm, mile, ft, inch, l, ml, gallon, C, F, K, hour, min, sec, mph, kmh, m/s"})
            from_cat, from_factor = units[from_u]
            to_cat, to_factor = units[to_u]
            if from_cat != to_cat:
                return jsonify({"reply": f"Cannot convert {from_u} to {to_u} — different categories ({from_cat} vs {to_cat})."})
            if from_cat == "temp":
                if from_factor == "c": celsius = val
                elif from_factor == "f": celsius = (val - 32) * 5/9
                else: celsius = val - 273.15
                if to_factor == "c": result = celsius
                elif to_factor == "f": result = celsius * 9/5 + 32
                else: result = celsius + 273.15
                reply = f"**Unit Conversion**\n\n{val} {from_u} = {result:.2f} {to_u}"
            else:
                base_val = val * from_factor
                result = base_val / to_factor
                reply = f"**Unit Conversion**\n\n{val} {from_u} = {result:.4f} {to_u}"
            return jsonify({"reply": reply})

        else:
            return jsonify({"error": f"Unknown live tool: {action}"}), 400
    except requests.exceptions.HTTPError as e:
        body = e.response.text[:300] if e.response is not None else ""
        return jsonify({"error": f"API error: {body}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Static file routes -----------------------------------------------------
@app.route("/manifest.json")
def manifest(): return send_from_directory(app.static_folder, "manifest.json")
@app.route("/sw.js")
def sw(): return send_from_directory(app.static_folder, "sw.js")
@app.route("/icon.png")
def icon(): return send_from_directory(app.static_folder, "icon.png")
@app.route("/marked.min.js")
def marked(): return send_from_directory(app.static_folder, "marked.min.js")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
