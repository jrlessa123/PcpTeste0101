from fastapi import APIRouter, HTTPException, Query

from mypcpweb.backend.adapters.protheus_sql_adapter import ProtheusSQLAdapter
from mypcpweb.backend.api.adapters.protheus_client import ProtheusClient
from mypcpweb.backend.config import AppConfig

router = APIRouter(prefix="/protheus", tags=["protheus"])

_client = ProtheusClient()
_sql_adapter = ProtheusSQLAdapter(AppConfig.from_env())


@router.get("/items")
def get_items(use_sql_fallback: bool = Query(default=True)):
    try:
        return _client.get_items()
    except RuntimeError as exc:
        if use_sql_fallback:
            return _sql_adapter.get_items()
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/stock")
def get_stock(armazem: str = Query(default="01"), use_sql_fallback: bool = Query(default=True)):
    try:
        return _client.get_stock(warehouse=armazem)
    except RuntimeError as exc:
        if use_sql_fallback:
            return _sql_adapter.get_stock(armazem=armazem)
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/requisitions")
def post_requisition(payload: dict):
    try:
        erp_request_id = _client.post_requisition(payload)
        return {"erp_request_id": erp_request_id}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
