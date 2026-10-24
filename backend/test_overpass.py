import httpx
import json

query = """[out:json][timeout:15];
(
  nwr["sport"="cricket"](around:15000,12.9698,77.75);
  nwr["leisure"="pitch"]["sport"="cricket"](around:15000,12.9698,77.75);
  nwr["leisure"="sports_centre"](around:12000,12.9698,77.75);
  nwr["leisure"="pitch"](around:8000,12.9698,77.75);
);
out center tags 30;"""

try:
    r = httpx.post(
        "https://overpass-api.de/api/interpreter",
        data={"data": query},
        headers={"User-Agent": "Fieldwise-Outdoor/1.0 (https://csre.iitb.ac.in)"},
        timeout=15.0
    )
    print("Status:", r.status_code)
    elements = r.json().get("elements", [])
    print("Found elements:", len(elements))
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("name:en")
        if name:
            lat = el.get("lat") or el.get("center", {}).get("lat")
            lon = el.get("lon") or el.get("center", {}).get("lon")
            print(f" - {name} ({lat:.4f}, {lon:.4f}) | sport: {tags.get('sport')} | leisure: {tags.get('leisure')}")
except Exception as e:
    print("Error:", e)
