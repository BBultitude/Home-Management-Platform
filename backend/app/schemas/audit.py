"""
Audit Log Schemas
Request and response models for audit log API
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

from app.models.audit_log import EventType, Severity


class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: int
    event_type: EventType
    user_id: Optional[int]
    username: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[int]
    details: Dict[str, Any]
    severity: Severity
    timestamp: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    """Schema for list of audit logs with pagination"""
    logs: list[AuditLogResponse]
    total: int = Field(..., description="Total number of logs matching filters")
    limit: int = Field(..., description="Number of logs returned")
    offset: int = Field(..., description="Pagination offset")

    @property
    def has_more(self) -> bool:
        """Check if there are more logs available"""
        return self.offset + self.limit < self.total

    model_config = {"from_attributes": True}
