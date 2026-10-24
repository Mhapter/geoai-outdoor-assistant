# Fieldwise — Your Outdoor Intelligence Assistant
### GeoAI Hackathon @ CSRE, IIT Bombay (2026)

Fieldwise is a real, evidence-grounded geospatial decision support web application that answers:
- **Where should I go for an outdoor activity?**
- **What is the best time to go?**
- **Which nearby locations have the most suitable conditions?**
- **How do weather, air quality, wind, daylight, roads, vegetation, water bodies, and nearby industrial areas affect the recommendation?**
- **What should I carry and prepare?**
- **What risks or conditions should I watch for?**
- **When should I avoid the activity?**

Fieldwise pairs a deterministic spatio-temporal reasoning engine (OpenStreetMap Overpass API, Open-Meteo hourly weather/AQI, OSRM routing) with an open-weights Small Language Model (**`Qwen/Qwen2.5-1.5B-Instruct`**, $\le$ 3B parameters) to produce verified, zero-hallucination recommendations.

---

## 1. Disclosed Base Model (Deliverable #2 Mandate)

| Specification | Implementation Detail |
| :--- | :--- |
| **Model ID** | [`Qwen/Qwen2.5-1.5B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) *(Configurable via `GEOAI_MODEL_ID`)* |
| **Active Parameters** | **1.54 Billion** (Strictly within the hackathon's $\le$ 3B limit) |
| **Weights License** | **Apache 2.0** (Open-source weights) |
| **Inference Mode** | Run locally via Hugging Face Transformers (`from_pretrained`). Large hosted models (GPT-4, Claude, Gemini Pro) are **not** used anywhere in the running assistant. |
| **Model Card & Repo** | Full model card and upload automation available in [`model_card/`](model_card/). |

---

## 2. Disclosed Live Data Sources & Attribution

Nothing is pre-computed, hardcoded, or fabricated. Every query fetches live telemetry at query time:

| Data Type | Primary Source | Protocol / Endpoint | Attribution / License |
| :--- | :--- | :--- | :--- |
| **Venues & Spatial Context** | OpenStreetMap | Overpass API & Photon | *© OpenStreetMap contributors (ODbL)* |
| **Geocoding & Gazetteer** | Photon, Open-Meteo & Nominatim | REST Search Endpoints | *Open-Meteo & © OpenStreetMap contributors* |
| **Hourly Weather Forecast** | Open-Meteo | Forecast API (temp, wind, rain, UV) | *Open-Meteo (CC-BY 4.0)* |
| **Hourly Air Quality** | Open-Meteo | Air Quality API (US AQI EPA Scale, PM2.5, PM10) | *Open-Meteo & Copernicus (CAMS)* |
| **Transit & Driving Duration** | OSRM | Route Service (free-flow road network) | *OSRM / © OpenStreetMap contributors* |

---

## 3. Supported Activities (All 10 Hackathon Mandatory Pursuits + Supplemental)

Fieldwise implements customized meteorological and spatial sensitivity thresholds for:
1. **Running or jogging** (Aerobic air quality, thermal comfort, road exhaust buffers)
2. **Cycling (leisure or commute)** (Crosswind stability, road classifications, rain slickness)
3. **Golf** (Multi-hour daylight, ball flight crosswind limits, UV accumulation)
4. **Recreational cricket** (Turf dry footing, daylight visibility, outfield moisture)
5. **Outdoor football or five-a-side** (Heat exhaustion thresholds, non-slip turf)
6. **Outdoor tennis** (Wind drift limits, court traction, glare protection)
7. **Hiking or nature walks** (Trail footing, daylight completion before sunset, rain shells)
8. **Picnics or park outings** (Shade canopies, calm breeze, green buffers)
9. **Outdoor events or gatherings** (Audiovisual rain contingency, crowd shelters)
10. **Outdoor photography & sunset** (Golden hour low-angle sunlight, horizon haze, tripod stability)
*Supplemental: Swimming, Badminton, Basketball, Fitness & Yoga, Skating, Boating, and General Outings.*

### Personal Health & Demographic Profiles
- **Asthma / Respiratory Sensitivity:** Tightens US AQI threshold to $\le 75$, doubles downwind highway plume penalties, mandates rescue inhaler in carry checklist.
- **Senior Citizens / Elderly Parents:** Enforces max temperature $\le 31^\circ\text{C}$, shade canopy buffers, avoids peak midday UV.
- **Children / Kids Outings:** Tightens AQI $\le 95$, distance buffers from arterial expressways, pediatric hydration guidance.
- **Pregnancy:** Low heat index, transit duration under 20 mins, level grades with accessible restrooms.

---

## 4. Repository Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point & CORS
│   │   ├── api/                     # Documented REST API endpoints
│   │   │   ├── health.py            # GET /api/health
│   │   │   ├── activities.py        # GET /api/activities
│   │   │   ├── sources.py           # GET /api/sources
│   │   │   └── recommendations.py   # POST /api/recommendations & POST /ask
│   │   ├── geo/                     # Spatial context & bearing math
│   │   │   └── spatial_context.py   # Overpass queries, downwind plume detection
│   │   ├── recommendations/         # Transparent scoring pipeline
│   │   │   ├── activity_profiles.py # 10+ activity thresholds
│   │   │   ├── personal_profiles.py # Asthma, senior, child, pregnancy profiles
│   │   │   └── scoring.py           # Multi-venue, multi-hour scoring function
│   │   ├── services/                # Modular async data retrieval
│   │   │   ├── geocoding_service.py # Multi-tier geocoder
│   │   │   ├── weather_service.py   # Open-Meteo weather forecast
│   │   │   ├── air_quality_service.py # Open-Meteo US AQI (EPA 0-500)
│   │   │   ├── routing_service.py   # OSRM road distance & duration
│   │   │   └── slm_service.py       # Qwen2.5-1.5B parser & grounded synthesis
│   │   └── schemas/
│   │       └── contracts.py         # Pydantic input/output contracts
│   ├── tests/                       # Automated test suite (24 passing tests)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                        # Next.js 16 (App Router) + TypeScript + Tailwind
│   ├── src/
│   │   ├── app/                     # Layout, globals.css & home page
│   │   ├── components/              # Distinctive outdoor-inspired UI components
│   │   │   ├── Navbar.tsx           # Brand, health status & modal triggers
│   │   │   ├── QueryForm.tsx        # NLP search bar + structured controls
│   │   │   ├── BestRecommendationCard.tsx # #1 ranked place & time card
│   │   │   ├── InteractiveMap.tsx   # Leaflet map with synchronized markers
│   │   │   ├── AlternativesList.tsx # Alternative venues compared
│   │   │   ├── HourlyTimeline.tsx   # Micro-climate conditions by hour
│   │   │   ├── EvidenceBreakdown.tsx# Favorable vs unfavorable factor audit
│   │   │   ├── PreparationGuide.tsx # What to carry, watch, and avoid
│   │   │   └── SourcesModal.tsx     # Live data provenance inspector
│   │   └── types/                   # TypeScript interfaces
│   └── Dockerfile
├── model_card/                      # Hugging Face submission deliverables
│   ├── README.md                    # Model card ready for Hugging Face Hub
│   └── upload_to_hf.py              # Automated Hub publishing script
├── docs/                            # Architecture & presentation
│   ├── architecture.md              # Technical methodology & math
│   └── presentation.html            # Deliverable #5 (6-slide presentation)
├── docker-compose.yml               # Local multi-service orchestration
├── .env.example                     # Environment template
└── README.md                        # Documentation
```

---

## 5. Quickstart: How to Run Locally

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ & npm (tested on Node v24, npm 11)

### Step 1: Start the Backend (Port 8000)

```bash
# In your terminal:
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The FastAPI engine boots on `http://127.0.0.1:8000`.
- Interactive Swagger Documentation: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/health`

### Step 2: Start the Frontend (Port 3000)

```bash
# In a second terminal:
cd frontend
npm run dev
```

Open your browser to **`http://localhost:3000`**.

---

## 6. Running Tests & Build Verification

### Backend Automated Test Suite

```bash
python -m pytest backend/tests -v
```

**Outcome: 24/24 tests passed** covering:
- All 10 mandatory activities & personal profile modifiers
- Multi-tier geocoder & gazetteer resolution
- Natural language query parser against all 10 hackathon example queries
- Spatial haversine, bearing, and downwind angular difference math
- Downwind highway plume penalty scoring
- FastAPI endpoints (`/api/health`, `/api/activities`, `/api/sources`, `/api/recommendations`)

### Frontend TypeScript & Production Build

```bash
cd frontend
npm run build
```

**Outcome: Zero errors**. TypeScript check and static route generation compile cleanly.

---

## 7. Public API Endpoints (Deliverable #1)

When exposing the backend to the judging panel over a public HTTPS tunnel:

```bash
# Option A: Cloudflare Tunnel (Free, no login required)
cloudflared tunnel --url http://127.0.0.1:8000

# Option B: Ngrok
ngrok http 8000

# Option C: Localtunnel
npx localtunnel --port 8000
```

### Key Endpoints

- `GET /api/health` — Readiness, active model ID, and data sources.
- `GET /api/activities` — All 10+ activity profiles and thresholds.
- `GET /api/sources` — Data provenance, license terms, and rate limits.
- `POST /api/recommendations` — Main grounded recommendation endpoint.
- `POST /ask` — Backward-compatible query endpoint.

### Example cURL Request

```bash
curl -X POST "http://127.0.0.1:8000/api/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Find a good place for jogging tomorrow morning within 10 km of Greater Noida",
    "personal_profiles": ["asthma"]
  }'
```

---

## 8. Hugging Face Deliverable (Deliverable #2)

Model configuration and card documentation are located in [`model_card/`](model_card/).

To publish to Hugging Face:
```bash
set HF_TOKEN=hf_your_write_token_here
python model_card/upload_to_hf.py your-username/fieldwise-geoai-slm
```

---

## 9. Presentation Slides (Deliverable #5)

A 6-slide presentation is available in [`docs/presentation.html`](docs/presentation.html). Open this file in any web browser to navigate with arrow keys during the evaluation interview.

---

## 10. Honest Limitations & Scope

1. **Free-Tier API Rate Limits:** OpenStreetMap Overpass and Open-Meteo APIs are rate-limited. Fieldwise uses a 30-minute disk cache (`.geoai_cache_v5`) to prevent throttling while respecting terms of service.
2. **OSRM Free-Flow Estimates:** OSRM estimates driving durations using speed limits and road classes; it does not model dynamic traffic delays without a live commercial telematics feed.
3. **Medical Disclaimer:** Personal profile filters (e.g. asthma, senior citizens) apply conservative thresholds to safeguard comfort and reduce pollutant inhalation. They do **not** constitute medical diagnosis or individual clinical advice.
