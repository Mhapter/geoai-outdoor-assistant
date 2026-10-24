import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.schemas.contracts import QueryRequest
from app.api.recommendations import create_recommendation

async def run():
    req = QueryRequest(
        question="i want to do swimming tomorrow near noida",
        location="Noida",
        activity="swimming",
        user_lat=28.5355,
        user_lon=77.3910
    )
    res = await create_recommendation(req)
    print("Origin:", res.origin)
    print("BEST RECOMMENDATION:", res.best_recommendation.venue_name)
    print("Score:", res.best_recommendation.score)
    print("Distance:", res.best_recommendation.distance_km, "km")
    print("Reasons Good:", res.best_recommendation.reasons_good)
    print("Photos count:", len(res.best_recommendation.images or []))
    for img in (res.best_recommendation.images or []):
        try:
            print(" -", img.get("title"), img.get("url"))
        except:
            pass

    print("\nALTERNATIVES:")
    for a in res.alternative_venues:
        print(" -", a.venue_name, "| dist:", a.distance_km, "km | score:", a.score)

if __name__ == "__main__":
    asyncio.run(run())
