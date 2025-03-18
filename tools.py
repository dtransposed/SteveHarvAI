"""
Tools that agents use for the 20 questions game.

This module defines output schemas and agent instances for specialized tasks
such as generating topics, validating answers, and asking questions.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field
from prompts import (
    SYSTEM_PROMPT_GENERATE_TOPIC,
    SYSTEM_PROMPT_GET_ANSWER,
    SYSTEM_PROMPT_GET_QUESTION,
    SYSTEM_PROMPT_VALIDATE_TOPIC_PROPOSAL,
)
from agents import Agent
from config import model_type_guesser, model_type_host, model_type_topic_proposal


# Base schemas
class BaseGameOutput(BaseModel):
    """
    Base schema for game outputs with common fields.

    :param reasoning: Explanation of the agent's reasoning
    """

    reasoning: str = Field(description="Explanation of the agent's reasoning process.")


# Tool schemas
class GetTopic(BaseGameOutput):
    """
    Schema for topic generation in the 20 questions game.

    :param category: General category of the topic
    :param sub_category: More specific subcategory
    :param topic: The actual topic to be guessed
    """

    category: str = Field(description="Briefly name the category of the topic.")
    sub_category: str = Field(description="Briefly name the sub-category of the topic.")
    topic: str = Field(
        description="A random concept or object that will be guessed by the Guesser."
    )


class ValidateAnswer(BaseGameOutput):
    """
    Schema for validating a topic proposal.

    :param is_correct: Whether the proposal matches the topic
    """

    reasoning: str = Field(description="Explain whether the topic proposal is correct.")
    is_correct: bool = Field(
        description="Whether the topic proposal matches the topic."
    )


class GetAnswer(BaseGameOutput):
    """
    Schema for generating answers to yes/no questions.

    :param answer: The yes/no answer to the question
    """

    reasoning: str = Field(
        description="Explain why you chose this answer. Does it align with the topic? How does it align with the rules of the game?"
    )
    answer: Literal["Yes", "No"] = Field(description="The answer to the last question.")


class GetQuestion(BaseGameOutput):
    """
    Schema for generating yes/no questions about the topic.

    :param question: The yes/no question
    :param topic_proposal: Optional topic proposal if the guesser wants to make a guess
    """

    reasoning: str = Field(
        description="Explain what do you know so far and why you chose this question. How does it help you guess the topic? How many steps do you have left?"
    )
    question: str = Field(
        description="A question about the topic. It should be a yes or no question. It should get you closer to guessing the topic."
    )
    topic_proposal: Optional[str] = Field(
        default=None, description="The topic you are trying to guess."
    )


# Agent instances
generate_topic_agent = Agent(
    name="generate_topic",
    model=model_type_topic_proposal,
    instructions=SYSTEM_PROMPT_GENERATE_TOPIC,
    output_type=GetTopic,
)

validate_topic_proposal_agent = Agent(
    name="validate_topic_proposal",
    model=model_type_host,
    instructions=SYSTEM_PROMPT_VALIDATE_TOPIC_PROPOSAL,
    output_type=ValidateAnswer,
)

get_answer_agent = Agent(
    name="get_answer",
    model=model_type_host,
    instructions=SYSTEM_PROMPT_GET_ANSWER,
    output_type=GetAnswer,
)

get_question_agent = Agent(
    name="get_question",
    model=model_type_guesser,
    instructions=SYSTEM_PROMPT_GET_QUESTION,
    output_type=GetQuestion,
)
