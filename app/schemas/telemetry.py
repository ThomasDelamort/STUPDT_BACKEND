from pydantic import BaseModel, Field


class TelemetryMetrics(BaseModel):
    specialistsConsulted: int = Field(default=1, ge=0, le=1000000)
    internalMeetings: int = Field(default=14, ge=0, le=1000000)
    minutesWasted: int = Field(default=6, ge=0, le=100000000)
    userSatisfaction: int = Field(default=-18, ge=-1000, le=1000)
    chaosMeter: int = Field(default=15, ge=0, le=1000)
