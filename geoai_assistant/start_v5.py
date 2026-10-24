"""
=============================================================================
  GeoAI Outdoor Intelligence Enterprise v5.2 — Launcher
  GeoAI Hackathon @ CSRE, IIT Bombay
=============================================================================
Launches the assistant API and interactive dashboard on http://127.0.0.1:8090/
"""
import os
import sys
import webbrowser
from threading import Timer

# Ensure Windows terminal supports UTF-8 / emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def main():
    import uvicorn

    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)

    port = int(os.getenv("GEOAI_PORT", "8090"))
    url = f"http://127.0.0.1:{port}/"
    docs_url = f"http://127.0.0.1:{port}/docs"
    health_url = f"http://127.0.0.1:{port}/health"

    print("=========================================================================")
    print("  🚀 GeoAI Outdoor Intelligence Enterprise v5.8 is starting...")
    print(f"  🌐 Interactive UI:     {url}")
    print(f"  📖 OpenAPI Docs:       {docs_url}")
    print(f"  🩺 Health Check:       {health_url}")
    print("  🏆 Powered by:         Qwen2.5-3B-Instruct (open-weights <=3B SLM)")
    print("  📡 Live Telemetry:     Open-Meteo, OpenStreetMap Overpass, OSRM")
    print("  ✨ Design Language:    Apple Human Interface Guidelines (Horizon / Light / Dark)")
    print("=========================================================================")

    Timer(1.5, lambda: webbrowser.open(url)).start()
    uvicorn.run("app:app", host="127.0.0.1", port=port, reload=False)


if __name__ == "__main__":
    main()
