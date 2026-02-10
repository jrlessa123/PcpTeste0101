from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class RequisitionResponse(BaseModel):
    id: int
    plan_id: int
    req_type: Literal["MP", "EMB"]
    status: Literal["DRAFT", "SENT", "ERROR"]
    erp_request_id: str | None = None
    created_at: datetime
