from __future__ import annotations

from mypcpweb.backend.api.adapters.protheus_client import ProtheusClient
from mypcpweb.backend.api.services.repository import PCPRepository
from mypcpweb.backend.config import AppConfig


class RequisitionService:
    def __init__(self, config: AppConfig):
        self.repository = PCPRepository(config)
        self.protheus_client = ProtheusClient()

    def create_requisition(self, plan_id: int, req_type: str):
        return self.repository.create_requisition(plan_id=plan_id, req_type=req_type)

    def send_to_protheus(self, requisition_id: int):
        payload = {"requisition_id": requisition_id}
        try:
            erp_request_id = self.protheus_client.post_requisition(payload)
            status = "SENT"
        except RuntimeError:
            erp_request_id = "PENDING_ENDPOINT"
            status = "ERROR"

        return self.repository.update_requisition_sent(
            requisition_id=requisition_id,
            erp_request_id=erp_request_id,
            status=status,
        )
