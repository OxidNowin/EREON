from fastapi import APIRouter, Response
from prometheus_client import (
    CollectorRegistry,
    generate_latest,
    multiprocess,
    CONTENT_TYPE_LATEST,
)


router = APIRouter(tags=["Metrics"])


@router.get("/healthcheck")
def healthcheck() -> dict:
    return {"status": "ok"}


@router.get("/metrics", summary="Получение метрик для prometheus")
def get_metrics():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    data = generate_latest(registry)
    return Response(data, media_type=CONTENT_TYPE_LATEST)
