#!/usr/bin/env python3
"""
Production startup script for the Tigaraksa Image Search API on Railway.
"""

import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False  # MUST be false on Railway
    )
