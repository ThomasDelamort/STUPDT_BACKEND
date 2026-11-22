from pydantic import BaseModel, Field


class BureaucracyFormRequest(BaseModel):
    problem: str = Field("", max_length=500, description="Submitted grievance description")
    reason: str = Field("", max_length=500, description="Submitted justification")
    notarizedCode: str = Field("", max_length=100, description="Notarized compliance code")
    confirmed: bool = Field(False, description="User confirmation state")


class BureaucracyFormResponse(BaseModel):
    success: bool
    stamped: bool
    error: str | None = None
