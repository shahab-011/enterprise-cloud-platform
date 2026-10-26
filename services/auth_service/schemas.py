from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictStr

Role = Literal["admin", "operator", "viewer"]


class DemoUser(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: str
    display_name: str
    role: Role


class TokenValidationRequest(BaseModel):
    token: StrictStr = Field(min_length=1, max_length=256)


class TokenValidationResponse(BaseModel):
    valid: Literal[True]
    user: DemoUser
    request_id: str
