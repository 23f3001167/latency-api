from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)

with open("q-vercel-latency.json", "r") as f:
    DATA = json.load(f)

class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: int

@app.post("/")
def analytics(req: RequestBody):

    result = {}

    for region in req.regions:

        rows = [
            r for r in DATA
            if r["region"] == region
        ]

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime"] for r in rows]

        result[region] = {
            "avg_latency": round(sum(latencies)/len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies,95)), 2),
            "avg_uptime": round(sum(uptimes)/len(uptimes), 2),
            "breaches": sum(
                1 for x in latencies
                if x > req.threshold_ms
            )
        }

    return result
