from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class PlanCreateRequest(BaseModel):
    ref_year: int = Field(ge=2020, le=2100)
    ref_week: int = Field(ge=1, le=53)
    criado_por: str = Field(min_length=2, max_length=100)


class PlanResponse(BaseModel):
    plan_id: int
    ref_year: int
    ref_week: int
    status: Literal["DRAFT", "CALCULATING", "FROZEN", "RELEASED"]
    criado_por: str
    criado_em: datetime


class PlanStatusResponse(BaseModel):
    plan_id: int
    status: Literal["DRAFT", "CALCULATING", "FROZEN", "RELEASED"]


class PlanResultItem(BaseModel):
    item_code: str
    quantity: float
    week: str
