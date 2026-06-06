from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json
import math

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load JSON data
DATA_FILE = Path(__file__).resolve().parent.parent / "q-vercel-latency.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    DATA = json.load(f)

class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: int

def percentile_95(values):
    values = sorted(values)

    if not values:
        return 0

    k = math.ceil(0.95 * len(values)) - 1
    return round(values[k], 2)

@app.get("/")
def home():
    return {"message": "Latency Analytics API Running"}

@app.post("/")
def analytics(req: RequestBody):

    result = {}

    for region in req.regions:

        rows = [r for r in DATA if r["region"] == region]

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        if not rows:
            result[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": percentile_95(latencies),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 2),
            "breaches": sum(
                1 for x in latencies
                if x > req.threshold_ms
            )
        }

    return result
