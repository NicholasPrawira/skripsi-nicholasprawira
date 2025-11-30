from fastapi import FastAPI, Query, HTTPException
import psycopg2
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# --- Load ENV & setup ---
load_dotenv()
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

# --- Koneksi ke database ---
def get_conn():
    return psycopg2.connect(SUPABASE_DB_URL)

# --- FastAPI app ---
app = FastAPI(title="Tigaraksa Image Search API")

# --- CORS supaya bisa diakses dari UI (Next.js/Framer) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "✅ API is running"}

@app.get("/search")
def search(q: str = Query(..., description="Cari gambar berdasarkan deskripsi")):
    try:
        conn = get_conn()
        cur = conn.cursor()

        # Query Postgres for pre-computed embeddings
        cur.execute("""
            SELECT prompt, image_url, clipscore, 1 - (embedding <=> %s::vector) AS similarity
            FROM images
            WHERE image_url IS NOT NULL
            ORDER BY embedding <=> %s::vector
            LIMIT 5;
        """, (q, q))  # Using text search instead of embedding computation

        results = cur.fetchall()
        cur.close()
        conn.close()

        if not results:
            raise HTTPException(status_code=404, detail="No similar images found.")

        # Return hasil ke UI
        return {
            "query": q,
            "results": [
                {
                    "prompt": r[0],
                    "image_url": r[1],
                    "clipscore": float(r[2]) if r[2] is not None else 0.0,
                    "similarity": round(float(r[3]), 3)
                }
                for r in results
            ],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run instructions:
# uvicorn server:app --reload