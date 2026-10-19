from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class FarmerQueryRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    farmer_id: Optional[str]
    query_type: str
    request_payload: dict[str, Any]
    response_payload: dict[str, Any]
    created_at: datetime


class FarmerQueryHistoryResponse(BaseModel):
    items: list[FarmerQueryRecord]
    count: int


class FarmerQueryHistoryParams(BaseModel):
    farmer_id: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=100)
