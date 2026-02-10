from fastapi import APIRouter, HTTPException, Query

from mypcpweb.backend.api.schemas.requisition import RequisitionResponse
from mypcpweb.backend.api.services.requisition_service import RequisitionService
from mypcpweb.backend.config import AppConfig

router = APIRouter(tags=["requisitions"])

_service = RequisitionService(AppConfig.from_env())


@router.post("/plans/{plan_id}/requisitions", response_model=RequisitionResponse)
def create_requisition(plan_id: int, tipo: str = Query(pattern="^(MP|EMB)$")):
    return _service.create_requisition(plan_id=plan_id, req_type=tipo)


@router.post("/requisitions/{requisition_id}/send-to-protheus", response_model=RequisitionResponse)
def send_to_protheus(requisition_id: int):
    data = _service.send_to_protheus(requisition_id)
    if not data:
        raise HTTPException(status_code=404, detail="Requisition not found")
    return data
