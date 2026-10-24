"""
Centralized Cache Manager for Fieldwise.
Seamlessly handles both local development and read-only serverless
environments such as Vercel and AWS Lambda by using /tmp when necessary.
"""

import os
import tempfile
import diskcache


def get_app_cache() -> diskcache.Cache:
    # Detect serverless environment or read-only filesystem
    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME") or os.getenv("SERVERLESS"):
        cache_dir = os.path.join(tempfile.gettempdir(), ".geoai_cache_v5")
    else:
        try:
            cache_dir = "./.geoai_cache_v5"
            os.makedirs(cache_dir, exist_ok=True)
        except (PermissionError, OSError):
            cache_dir = os.path.join(tempfile.gettempdir(), ".geoai_cache_v5")

    try:
        return diskcache.Cache(cache_dir)
    except Exception:
        fallback_dir = os.path.join(tempfile.gettempdir(), ".geoai_cache_v5")
        return diskcache.Cache(fallback_dir)


cache = get_app_cache()
