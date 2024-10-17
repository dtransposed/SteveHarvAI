"""
Message objects.
They facilitate sharing the information between agents and the environment
"""

from pydantic import BaseModel
from typing import Literal


class UserMessage(BaseModel):
    content: str
    role: Literal["user"] = "user"


class AssistantMessage(BaseModel):
    content: str
    role: Literal["assistant"] = "assistant"


class SystemMessage(BaseModel):
    content: str
    role: Literal["system"] = "system"


class StepMessage(BaseModel):
    step: int
    role: Literal["step"] = "step"
