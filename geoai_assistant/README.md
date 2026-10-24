# GeoAI Outdoor Intelligence Assistant (≤3B SLM)
### GeoAI Hackathon @ CSRE, IIT Bombay 2026

An intelligent geospatial advisor powered by an open-weights Small Language Model (**`Qwen/Qwen2.5-3B-Instruct`**, $\le$ 3B parameters) that recommends **where** and **when** to head outdoors, what to prepare, what to watch for, and when to avoid going.

The system combines deterministic geospatial math (OpenStreetMap Overpass API, Open-Meteo hourly weather/AQI, OSRM traffic routing) with an open SLM synthesis engine to deliver zero-hallucination recommendations tailored to individual health and demographic profiles.

---

## 1. Disclosed Base Model (Deliverable #2)

- **Model ID:** [`Qwen/Qwen2.5-3B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct)
- **Active Parameters:** 3.09 Billion (strictly adheres to the hackathon's $\le$ 3B limit)
- **Weights License:** Apache 2.0 (Open-source weights)
- **Inference Mode:** Run locally via Hugging Face `from_pretrained(...)`. Large hosted models (GPT-4, Claude, Gemini Pro) are **not** used anywhere in the running assistant.
- **Hugging Face Hub Repository:** Model card and configuration are provided in [`hf_model_card/README.md`](hf_model_card/README.md).

---

## 2. Disclosed Live Data Sources & Attribution

Nothing is pre-computed or static. Every query fetches live telemetry in real time:

| Data Type | Primary Source | Protocol / API | Attribution / Terms |
| :--- | :--- | :--- | :--- |
| **Venues & Spatial Context** | OpenStreetMap | Overpass API | *© OpenStreetMap contributors* (ODbL) |
| **Geocoding & Gazetteer** | Open-Meteo & Photon | REST Geocoding API | *Open-Meteo & © OpenStreetMap contributors* |
| **Hourly Weather Forecast** | Open-Meteo | Forecast API (temp, wind, UV, rain) | *Open-Meteo (CC-BY 4.0)* |
| **Hourly Air Quality** | Open-Meteo | Air Quality API (US AQI, PM2.5, PM10) | *Open-Meteo Atmospheric Model* |
| **Transit & Routing** | OSRM | Open Source Routing Machine | *OSRM / © OpenStreetMap contributors* |

---

## 3. How to Run Locally

### Step 1: Clone and Enter the Directory

```bash
cd geoai_assistant
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Launch the Assistant

```bash
python start_v5.py
```

This immediately boots the FastAPI engine on port **`8090`** (to bypass stale port-7860 processes) and automatically opens **`http://127.0.0.1:8090/`** in your default web browser.

---

## 4. Live API Endpoints (Deliverable #1)

When deployed or tunneled, the assistant provides the following public endpoints:

- **Interactive Dashboard:** `http://127.0.0.1:8090/`
- **Swagger Documentation:** `http://127.0.0.1:8090/docs`
- **Health & Attribution Check:** `GET /health`
- **Inference Query Endpoint:** `POST /ask`

### Keeping the Endpoint Live During Judging

To expose your local instance to the judging panel over a public HTTPS URL:

#### Option A: Cloudflare Tunnel (Free, No Sign-up required)
```bash
# In a separate terminal:
cloudflared tunnel --url http://127.0.0.1:8090
```

#### Option B: Ngrok
```bash
ngrok http 8090
```

#### Option C: Localtunnel
```bash
npx localtunnel --port 8090
```

Provide the generated HTTPS URL (e.g., `https://your-geoai-endpoint.trycloudflare.com/ask`) in your submission form.

---

## 5. API Usage & Example cURL Commands

### Health Check (`GET /health`)
```bash
curl -X GET "http://127.0.0.1:8090/health"
```
**Response:**
```json
{
  "status": "ok",
  "version": "5.2.0",
  "model_id": "Qwen/Qwen2.5-3B-Instruct",
  "attribution": "© OpenStreetMap contributors, Open-Meteo, OSRM"
}
```

### Query Endpoint (`POST /ask`)
```bash
curl -X POST "http://127.0.0.1:8090/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "I have mild asthma, where is good for a morning walk near Powai in the next two days?"}'
```

---

## 6. Verification of the 10 Hackathon Queries

All 10 example queries from the problem statement are handled with full context:

1. **Running in Koregaon Park:** `"Where can I go running tomorrow evening near Koregaon Park?"`  
   *Extracted:* Running, Koregaon Park, 10 km radius, Evening window (4–8 PM), Tomorrow.
2. **Kids' Cricket in Whitefield:** `"Best time this weekend for a kids' cricket match within 15 km of Whitefield?"`  
   *Extracted:* Cricket, Whitefield, 15 km radius, Weekend window, Child profile (extra hydration, sunscreen).
3. **Morning Walk with Mild Asthma:** `"I have mild asthma, where's good for a morning walk near Powai in the next two days?"`  
   *Extracted:* Walking, Powai, 6 km radius, Morning window (6–10 AM), Asthma profile (AQI $\le 75$, $2.5\times$ downwind highway penalty).
4. **Cycling Commute (Missing Location Guardrail):** `"Is it okay to cycle to work at 8 AM?"`  
   *Guardrail:* Detects missing location and politely asks for the city/commute route without hallucinating.
5. **Outdoor Birthday Party:** `"Planning an outdoor birthday party on Sunday afternoon in Pune, what should I keep in mind?"`  
   *Extracted:* Outdoor event, Pune, Afternoon window (12–4 PM), Sunday. Advises shade tents & hydration against midday heat.
6. **Golf near Andheri:** `"Good place and time for golf on Saturday within 40 km of Andheri?"`  
   *Extracted:* Golf, Andheri, 40 km radius, Saturday daylight.
7. **Sunset Photography in Bandra:** `"Where can I take sunset photos this evening around Bandra?"`  
   *Extracted:* Photography, Bandra West, Golden-hour sunset window (5–7:30 PM), coastal promenade alignment.
8. **Comparative Hiking Query:** `"Is Saturday or Sunday better for a hike near Lonavala?"`  
   *Extracted:* Hiking, Lonavala, Saturday vs. Sunday comparative evaluation across rainfall probability and wind vectors.
9. **Senior Parents Walking:** `"When is it safe for my parents to walk outdoors tomorrow in Bengaluru?"`  
   *Extracted:* Walking, Bengaluru, Senior profile (avoids peak UV $11:30\text{ AM} - 4:00\text{ PM}$, level shaded paths).
10. **Tennis after Work:** `"Outdoor tennis after work today near Hinjewadi, any good spots?"`  
    *Extracted:* Tennis, Hinjewadi, After-work window (5–8:30 PM), checks court lighting and crosswinds ($<20\text{ km/h}$).

---

## 7. Architecture & Spatio-Temporal Plume Reasoning

```
                   ┌───────────────────────────────────┐
                   │    Free-Form User Question        │
                   └─────────────────┬─────────────────┘
                                     │
                                     ▼
                   ┌───────────────────────────────────┐
                   │ NLP Intent & Guardrail Parser     │
                   │ (Activity, Location, Profile, Hr) │
                   └─────────────────┬─────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
┌──────────────────┐       ┌──────────────────┐        ┌──────────────────┐
│   Open-Meteo     │       │  OpenStreetMap   │        │      OSRM        │
│ Hourly Weather   │       │   Overpass API   │        │ Driving Travel   │
│   & US AQI       │       │ Venues & Hazards │        │  Time (Minutes)  │
└────────┬─────────┘       └─────────┬────────┘        └─────────┬────────┘
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     │
                                     ▼
                   ┌───────────────────────────────────┐
                   │ Spatio-Temporal Plume Engine      │
                   │ - Bearing & Dispersion Math       │
                   │ - Rush-hour Traffic Multipliers   │
                   │ - Health Profile Caps (Asthma/Age)│
                   └─────────────────┬─────────────────┘
                                     │
                                     ▼
                   ┌───────────────────────────────────┐
                   │ Small Language Model (Qwen2.5-3B) │
                   │ Zero-Hallucination Grounded Synth │
                   └─────────────────┬─────────────────┘
                                     │
                                     ▼
                   ┌───────────────────────────────────┐
                   │ Interactive Leaflet Map & Report  │
                   └───────────────────────────────────┘
```

---

## 8. License & Attribution

- Code is licensed under the **Apache License 2.0**.
- Map data © [OpenStreetMap](https://www.openstreetmap.org/) contributors.
- Weather data powered by [Open-Meteo](https://open-meteo.com/).
