# GeoAI Outdoor Intelligence Assistant — Presentation Deck
### CSRE, IIT Bombay — GeoAI Hackathon 2026 (5-Slide Deck)

---

## Slide 1: The Problem & Our Approach

### The Real-World Dilemma
- **Current Limitations:** Conventional weather apps provide single-number city averages (e.g., *"Mumbai 31°C, AQI 115"*), and navigation maps show static venues without environmental context.
- **What People Actually Need:** Outdoor decisions require **joint spatio-temporal reasoning**:
  - *Which specific park is sheltered from expressway exhaust plumes when the morning breeze shifts?*
  - *Is a ground 30 minutes away worth visiting during rush-hour congestion?*
  - *What safety limits apply to a child, a pregnant woman, or someone with mild asthma?*

### Our Approach: Neuro-Symbolic GeoAI Architecture
- **Deterministic Spatial & Environmental Engine:** Live OpenStreetMap Overpass extraction, Open-Meteo hourly meteorology, and OSRM routing.
- **Open-Weights $\le$3B Small Language Model (`Qwen2.5-3B-Instruct`):** Runs locally to parse unstructured queries, enforce strict guardrails, and synthesize grounded recommendations without hallucination.

```
+-------------------------------------------------------------------------------+
|  User Query: "Mild asthma, where's good for a morning walk near Powai?"       |
+---------------------------------------+---------------------------------------+
                                        |
  [Live OSM Features] + [Open-Meteo Hourly Wind/AQI] + [OSRM Rush-Hour Transit]
                                        |
                                        v
+-------------------------------------------------------------------------------+
|  Spatio-Temporal Plume Math: Downwind Highway Penalty + Canopy Buffer Credit  |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|  <=3B SLM Synthesis: #1 Nirvana Park @ 6:30 AM (AQI 58, Upwind of JVLR)      |
+-------------------------------------------------------------------------------+
```

---

## Slide 2: End-to-End Architecture

Our pipeline executes in four real-time stages with zero pre-computed static databases:

```
[ Stage 1: Intent & Guardrails ]
  │ Parses 10+ outdoor activities, location, radius, time windows, and personal profiles.
  │ Enforces strict guardrails for missing locations or out-of-scope requests.
  ▼
[ Stage 2: Asynchronous Live Telemetry Gathering ]
  │ Parallel httpx queries to OpenStreetMap Overpass API, Open-Meteo Weather/AQI, & OSRM.
  │ Implements 30-minute diskcache TTL to respect open-source API rate limits.
  ▼
[ Stage 3: Spatio-Temporal & Downwind Plume Engine ]
  │ Calculates exact bearing between arterial roads / industrial zones and venues.
  │ Models plume dispersion relative to wind direction vectors and rush-hour traffic.
  │ Dynamically tightens AQI and thermal caps for vulnerable health profiles.
  ▼
[ Stage 4: Grounded SLM Synthesis & Visualization ]
  │ Qwen2.5-3B synthesizes actionable advice strictly backed by the live JSON payload.
  │ Interactive Leaflet map visualizes venue suitability, wind vectors, and transit lines.
```

---

## Slide 3: Worked Example — Powai Morning Walk with Mild Asthma

### Query
> *"I have mild asthma, where's good for a morning walk near Powai in the next two days?"*

### Multi-Venue & Temporal Evaluation Matrix

| Candidate Venue | Distance & Transit | Time Evaluated | US AQI / PM2.5 | Wind & Plume Status | Suitability Score | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Nirvana Park, Hiranandani** | 1.8 km (6 min drive) | **Fri 6:30 AM** | **58 / 16 µg/m³** | **NE breeze (Upwind of JVLR)** | **92 / 100** | **🏆 #1 Optimal Choice** |
| **Powai Lake Promenade** | 1.2 km (4 min drive) | Fri 8:00 AM | 78 / 24 µg/m³ | Calm, minor JVLR crosswind | 76 / 100 | Good early; avoid after 8 AM |
| **JVLR Arterial Linear Park** | 2.1 km (14 min rush) | Fri 8:30 AM | 108 / 38 µg/m³ | **Downwind of highway traffic** | **44 / 100** | **🛑 AVOID: Severe Plume** |

### Tailored Practical Advice
- **What to Carry:** Prescribed fast-acting rescue inhaler (albuterol), N95 respirator mask during road transit.
- **What to Watch For:** Wind calm after 7:45 AM leading to localized particulate buildup along major roads.
- **When to Avoid:** 8:00 AM – 10:00 AM rush-hour peak where traffic exhaust plumes drift southwest.

---

## Slide 4: Our $\le$3B Model & Zero-Hallucination Design

### Model Specifications
- **Base Architecture:** `Qwen/Qwen2.5-3B-Instruct` (3.09B active parameters).
- **Hosting:** Public Hugging Face Hub repository with full model card and Apache 2.0 license.
- **Local Inference:** Loaded via Hugging Face `from_pretrained(...)` on CPU / CUDA.

### Elimination of Hallucination via Strict Grounding
1. **No Memorization Dependency:** The small model is intentionally prevented from relying on outdated parametric memory for local weather or road layouts.
2. **Context-Injected Evidence Payload:** The engine feeds structured JSON containing exact calculated values:
   - Real OSRM driving minutes and distances.
   - Live Open-Meteo temperatures, relative humidity, and precipitation probability.
   - Real-time US AQI and $\text{PM}_{2.5}$ concentration.
   - Vector angular differential between wind direction and pollution sources.
3. **Guardrail Enforcements:** Incomplete queries (e.g. *"Is it okay to cycle to work at 8 AM?"*) trigger an immediate request for origin/destination rather than generating fictitious routes.

---

## Slide 5: Honest Limitations & Future Road Map

### Current Limitations
1. **OSM Tag Completeness:** Informal neighborhood grounds in smaller tier-2/3 Indian cities often lack `sport=*` or `leisure=pitch` tags in OpenStreetMap.
2. **Angular Plume Approximation:** The plume dispersion engine uses angular sector matching ($\pm 45^\circ$) and distance attenuation rather than 3D micro-scale Computational Fluid Dynamics (CFD).
3. **Heuristic Traffic Modeling:** Rush-hour transit times are scaled via empirical time-of-day multipliers over OSRM free-flow routing rather than live per-vehicle GPS probes.

### Future Enhancements
- **Direct Indian Open Data Ingestion:** Integrate real-time CPCB (Central Pollution Control Board) ground monitoring stations via `data.gov.in` for hyper-local calibration.
- **Domain-Specific LoRA Fine-Tuning:** Fine-tune `Qwen2.5-3B` on curated Indian regional outdoor terminology and bilingual prompts (English + Hindi/regional languages).
- **Micro-Topography Integration:** Ingest SRTM/OpenTopography elevation profiles for gradient slope analysis on hiking and cycling routes.
