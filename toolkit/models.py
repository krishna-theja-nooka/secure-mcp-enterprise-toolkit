from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("*", mode="before")
    @classmethod
    def reject_controls(cls, value):
        if isinstance(value, str) and any(ord(c) < 32 for c in value):
            raise ValueError("Control characters are not allowed")
        return value


class Analytics(Input):
    metric: Literal["fleet_summary", "maintenance_by_region"] = "fleet_summary"
    region: Literal["All", "Austin", "Dallas", "Denver"] = "All"


class Lookup(Input):
    query: str = Field(min_length=2, max_length=200)
    limit: int = Field(default=3, ge=1, le=5, strict=True)


class Proposal(Input):
    vehicle_id: str = Field(pattern=r"^EV-\d{3}$")
    title: str = Field(min_length=5, max_length=120)
    description: str = Field(min_length=10, max_length=1000)
    priority: Literal["normal", "urgent"] = "normal"


class Decision(Input):
    decision: Literal["approve", "reject"]


class ToolResult(BaseModel):
    trace_id: str
    status: Literal["ok", "error"]
    data: dict = Field(default_factory=dict)
    error: str | None = None
    code: str | None = None
    synthetic: bool = True
