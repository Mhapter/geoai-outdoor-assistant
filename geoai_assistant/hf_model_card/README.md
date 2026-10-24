---
license: apache-2.0
base_model: Qwen/Qwen2.5-3B-Instruct
language:
  - en
tags:
  - geoai
  - outdoor-intelligence
  - small-language-model
  - geospatial-reasoning
  - spatio-temporal
  - zero-hallucination
  - micro-climate
  - qwen2.5
pipeline_tag: text-generation
library_name: transformers
---

# GeoAI Outdoor Intelligence SLM (≤3B Parameters)
**CSRE, IIT Bombay — GeoAI Hackathon 2026**

This repository hosts the configuration, model card, and neuro-symbolic inference pipeline for the **GeoAI Outdoor Intelligence Assistant**, powered by the open-weights **`Qwen/Qwen2.5-3B-Instruct`** small language model (3.09 billion parameters).

The model is paired with a deterministic geospatial and meteorological reasoning engine that fetches live OpenStreetMap features, Open-Meteo hourly weather/AQI, and OSRM travel durations, synthesizing zero-hallucination outdoor recommendations across space and time.

---

## 1. Model Summary

- **Base Model:** [`Qwen/Qwen2.5-3B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct)
- **Parameter Count:** 3.09 Billion parameters (strictly complies with the hackathon limit of $\le$ 3B active parameters)
- **Architecture:** Causal Language Model with RoPE (Rotary Positional Embeddings), RMSNorm, SwiGLU activations, and Grouped Query Attention (GQA).
- **License:** Apache 2.0 (Open-source)
- **Intended Use:** Spatio-temporal outdoor activity recommendation, micro-climate reasoning, highway/industrial plume avoidance, and personalized health guardrailing.

---

## 2. Why a Small Language Model (≤3B)?

In geospatial and meteorological planning, large hosted models (e.g. GPT-4, Claude) suffer from severe hallucinations when guessing localized weather or park geometries from stale pre-training memory. 

By enforcing a **small, open-weights model ($\le$ 3B)**, the architecture strictly decouples:
1. **Mathematical & Spatio-Temporal Fact Retrieval (Deterministic)**: OpenStreetMap Overpass API, Open-Meteo hourly telemetry, and OSRM drive-times.
2. **Contextual Synthesis & Conversational Advisory (SLM)**: The $\le$3B model reasons exclusively over the live structured JSON evidence payload, guaranteeing that every temperature, AQI, distance, and wind vector is grounded in real-time data.

---

## 3. Quickstart & Usage

### Installation

```bash
pip install transformers torch accelerate huggingface-hub
```

### Loading with `from_pretrained(...)`

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto" if torch.cuda.is_available() else None,
    trust_remote_code=True
)
model.eval()

# GeoAI Grounded Inference Example
system_prompt = (
    "You are GeoAI Outdoor Advisor, powered by a <=3B Small Language Model. "
    "Advise the user using ONLY the live fetched data in the JSON evidence. "
    "Never invent weather, AQI, or venue names."
)

user_prompt = """
User Question: I have mild asthma, where's good for a morning walk near Powai in the next two days?

Live Evidence (JSON):
{
  "best_recommendation": {
    "venue_name": "Nirvana Park, Powai",
    "hour_label": "Fri 24 Oct, 06:30 AM",
    "score": 92.4,
    "temp_c": 22.4,
    "us_aqi": 58,
    "pm25": 16.2,
    "wind_compass": "NE",
    "downwind_status": "Upwind / Clear of JVLR",
    "travel_mins": 8.5
  },
  "what_to_carry": ["Fast-acting rescue inhaler", "N95 mask for road transit"],
  "data_sources": ["© OpenStreetMap contributors", "Open-Meteo", "OSRM"]
}
"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
]

prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=400, temperature=0.15)

response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
print(response)
```

---

## 4. Supported Activities & Personal Profiles

### Activities (10 Reference Activities)
1. **Running / Jogging** (parks, athletic tracks, greenways)
2. **Cycling** (leisure or commute routes, cycleways)
3. **Golf** (fairways, driving ranges, daylight sensitive)
4. **Cricket** (recreational matches, pitches, open grounds)
5. **Outdoor Football / 5-a-side** (turfs, recreational pitches)
6. **Outdoor Tennis** (courts, low cross-wind requirements $<20\text{ km/h}$)
7. **Hiking / Nature Walks** (trails, nature reserves, elevation)
8. **Picnic / Outing** (shaded gardens, lakeside picnic sites)
9. **Outdoor Events & Gatherings** (open lawns, community venues, shade)
10. **Outdoor Photography** (viewpoints, golden-hour alignment near sunset/dawn)

### Health & Demographic Profiles
- **Mild Asthma / Respiratory**: Tightens AQI tolerance ($\le 75$), enforces $2.5\times$ penalty for venues downwind of expressways/industrial zones, mandates rescue inhaler advice.
- **Senior Citizens / Parents**: Avoids peak midday UV ($11:30\text{ AM} - 4:00\text{ PM}$), prioritizes shaded level walking paths.
- **Children / Kids**: Accounts for higher ventilation rates per kg body weight, filters out highway corridors.
- **Pregnancy**: Limits heat index, requires travel times $<20$ minutes and restroom access.

---

## 5. Spatio-Temporal Downwind Plume Engine

The model operates alongside an angular dispersion physics module:
- Computes bearing $\theta_{\text{hazard} \to \text{venue}}$ from arterial expressways (`highway=motorway|trunk|primary`) and industrial clusters (`landuse=industrial`).
- Measures angle differential against live wind direction $\mathbf{w}_{\text{dir}}$.
- If $|\mathbf{w}_{\text{dir}} - \theta| \le 45^\circ$, the venue is marked as **Downwind Plume Hazard** with emissions amplified during rush hours ($8-10\text{ AM}, 5-8\text{ PM}$).

---

## 6. Disclosed Live Data Sources & Attribution

All recommendations are backed by real-time open data:
- **OpenStreetMap** (Overpass API, Nominatim, Photon): Map features, recreation grounds, arterial roads, and water bodies. *Attribution: © OpenStreetMap contributors.*
- **Open-Meteo**: Hourly weather forecast (temperature, humidity, precipitation, wind speed/direction, UV) and air quality (US AQI, $\text{PM}_{2.5}$, $\text{PM}_{10}$).
- **OSRM (Open Source Routing Machine)**: Driving transit duration and free-flow routing.

---

## 7. Limitations & Ethical Considerations

- **Informal Grounds in OSM**: Tagging density varies by municipal jurisdiction. Unmapped school or neighborhood grounds may not appear in Overpass queries.
- **Micro-scale Obstacles**: The model utilizes sector bearing and distance decay approximations rather than 3D building canyon computational fluid dynamics (CFD).
- **Medical Disclaimer**: Health advisories are decision-support guidelines and do not replace personalized medical advice from a physician.
