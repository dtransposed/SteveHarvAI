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

round_message = """This is round {round_number}/{max_num_rounds} of the game. Do not do anything with this message, just acknowledge it."""
topic_message = """Use an appropriate tool to provide a unique and random topic for a game of 20 questions. Here is a unique seed to ensure randomness and diversity: '{unique_id}'. Ensure the topic is diverse, creative, and comes from a broad range of categories."""
question_message = """Generate a question that helps you guess the topic. Be creative and think about the best question to ask."""