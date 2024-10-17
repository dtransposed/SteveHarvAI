"""
Tools that the agents can use.
"""

from pydantic import BaseModel, Field


# Used by the Host
class GetTopic(BaseModel):
    """
    Come up with a topic for the game of 20 questions.
    """

    reasoning: str = Field(
        description="Explain why you chose this topic. Make sure to pick a different topic each time (use unique seed provided)."
    )
    category: str = Field(description="Briefly name the category of the topic.")
    sub_category: str = Field(description="Briefly name the sub-category of the topic.")
    topic: str = Field(
        description="A random concept or object that will be guessed by the Guesser. "
    )


# Used by the Host
class ValidateAnswer(BaseModel):
    """
    Validate if the topic was guessed correctly.
    """

    reasoning: str = Field(
        description="Explain why whether the topic proposal is correct."
    )
    is_correct: bool = Field(
        description="Whether the topic proposal matches the topic."
    )


# Used by the Host
class GetAnswer(BaseModel):
    """
    Generate an answer to the question.
    """

    reasoning: str = Field(
        description="Explain why you chose this answer. Does it align with the topic and rules of the game?"
    )
    answer: str = Field(
        description="The answer to the last question. It should be a `Yes` or `No` answer."
    )


# Used by the Guesser
class GetQuestion(BaseModel):
    """
    Generate a question about the topic.
    """

    reasoning: str = Field(
        description="Explain what do you know so far and why you chose this question. How does it help you guess the topic? How many steps do you have left?"
    )
    question: str = Field(
        description="A question about the topic. It should be a yes or no question. It should get you closer to guessing the topic."
    )
    topic_proposal: str | None = Field(
        description="The topic you are trying to guess. You are encouraged to take wild guesses and come up with topic proposals, especially when there are only a few steps left."
    )
