import os
import time
import uuid
from typing import List, Dict, Optional
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel, Field

app = FastAPI(title="Model API", version="0.1.0")
MODEL_VERSION = os.getenv("MODEL_VERSION", "v2026.01")


@app.middleware("http")
async def request_logging(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    start = time.time()
    response: Response = await call_next(request)
    elapsed_ms = int((time.time() - start) * 1000)
    response.headers["X-Request-Id"] = request_id
    print(f"{request.method} {request.url.path} status={response.status_code} "
          f"latency_ms={elapsed_ms} requestId={request_id}")
    return response


class ModelRecommendRequest(BaseModel):
    requestId: str
    userId: str
    scene: str
    numItems: int = Field(ge=1, le=50)
    candidateItems: Optional[List[str]] = None
    context: Optional[Dict[str, object]] = None


class ScoreItem(BaseModel):
    itemId: str
    score: float


class ModelRecommendResponse(BaseModel):
    requestId: str
    modelVersion: str
    scores: List[ScoreItem]


@app.post("/model/recommend", response_model=ModelRecommendResponse)
def recommend(req: ModelRecommendRequest) -> ModelRecommendResponse:
    candidates = req.candidateItems or [f"p{i:03d}" for i in range(1, req.numItems * 5 + 1)]
    top = candidates[: req.numItems]
    scores = [ScoreItem(itemId=item, score=1.0 - idx * 0.01) for idx, item in enumerate(top)]
    return ModelRecommendResponse(
        requestId=req.requestId,
        modelVersion=MODEL_VERSION,
        scores=scores,
    )


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "modelVersion": MODEL_VERSION}
