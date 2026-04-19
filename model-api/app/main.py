import os
import json
import time
import hashlib
import contextvars
from typing import List, Dict, Optional
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel, Field

app = FastAPI(title="Model API", version="0.1.0")
MODEL_VERSION = os.getenv("MODEL_VERSION", "v2026.01")
REQUEST_ID_CTX: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")


def _mask_identifier(value: Optional[str]) -> str:
    if not value:
        return "redacted"
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return f"h:{digest[:12]}"


def _log_event(payload: Dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False), flush=True)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id") or "unknown"
    REQUEST_ID_CTX.set(request_id)
    start = time.time()
    response: Response = await call_next(request)
    elapsed_ms = int((time.time() - start) * 1000)
    response.headers["X-Request-Id"] = request_id
    _log_event({
        "event": "model_api_access",
        "service": "model-api",
        "requestId": request_id,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "latencyMs": elapsed_ms,
        "userId": "redacted",
        "itemId": "redacted",
        "requestBody": "[REDACTED]",
    })
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
    _log_event({
        "event": "model_recommend_received",
        "service": "model-api",
        "requestId": REQUEST_ID_CTX.get(),
        "userId": _mask_identifier(req.userId),
        "itemId": "redacted",
        "requestBody": "[REDACTED]",
    })
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
