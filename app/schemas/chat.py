from pydantic import BaseModel, Field
from typing import List, Optional, Any


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User inquiry text")
    departmentId: str = Field("intake", max_length=50, description="Current department ID")
    history: Optional[List[Any]] = Field(default=[], description="Recent conversation turns")


class QuickReplySuggestion(BaseModel):
    label: str
    value: str


class ChatResponse(BaseModel):
    reply: str
    departmentId: str
    departmentName: Optional[str] = None
    departmentRole: Optional[str] = None
    departmentBadge: Optional[str] = None
    blame: Optional[str] = None
    suggestedQuickReply: Optional[QuickReplySuggestion] = None
