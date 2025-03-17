"""
Tools that the agents can use.
"""

from typing import Any
from pydantic import BaseModel, Field
from agents import Agent, RunContextWrapper, function_tool, Runner

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
    
get_topic_tool = Agent(
    name="get_topic",
    instructions="Come up with a topic for the game of 20 questions.",
    output_type=GetTopic,
).as_tool(
    tool_name="get_topic",
    tool_description="Come up with a topic for the game of 20 questions.",
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
    
@function_tool
async def get_validate_topic_proposal_tool(ctx: RunContextWrapper[Any]) -> ValidateAnswer:
    agent = Agent(
        name="get_validate_topic_proposal",
        instructions="You are helping in the game of 20 questions. You are given a topic proposal and a topic. You need to assess whether the topic proposal is related to the topic or not. Do not be too strict, i.e. if topic_proposal is `Husky`, and the topic is `Dog`, validate it as correct. Some goes for `wildlife photography` and `nature photography`. But also don't be too lenient, i.e. if topic_proposal is `musical instrument`, and the topic is `violin`, reject it, as it is not a specific enough topic proposal.",
        output_type=ValidateAnswer,
    )
    result = await Runner.run(agent, f"Topic proposal: {ctx.context['topic_proposal']}. Topic: {ctx.context['topic']}")
    result = ValidateAnswer.model_validate_json(result.new_items[0].raw_item.content[0].text)
    return f"{result.reasoning}|{result.is_correct}"


# Used by the Host
class GetAnswer(BaseModel):
    reasoning: str = Field(
        description="Explain why you chose this answer. Does it align with the topic? How does it align with the rules of the game?"
    )
    answer: str = Field(
        description="The answer to the last question. It should be a `Yes` or `No` answer."
    )


@function_tool
async def get_answer_tool(ctx: RunContextWrapper[Any]) -> GetAnswer:
    agent = Agent(
        name="get_answer",
        instructions="You are helping in the game of 20 questions. You are given a question and a topic. You need to assess whether the question is strictly related to the topic or not. Provide helpful and focused answers that will guide the other side to guess the topic. ",
        output_type=GetAnswer,
    )
    result = await Runner.run(agent, f"Question: {ctx.context['question']}. Topic: {ctx.context['topic']}")
    result = GetAnswer.model_validate_json(result.new_items[0].raw_item.content[0].text)
    return f"{result.reasoning}|{result.answer}"

# Used by the Guesser
class GetQuestion(BaseModel):
    reasoning: str = Field(
        description="Explain what do you know so far and why you chose this question. How does it help you guess the topic? How many steps do you have left?"
    )
    question: str = Field(
        description="A question about the topic. It should be a yes or no question. It should get you closer to guessing the topic."
    )
    topic_proposal: str | None = Field(
        description="The topic you are trying to guess. You are encouraged to take wild guesses and come up with topic proposals, especially when there are only a few steps left."
    )

@function_tool
async def get_question_tool(ctx: RunContextWrapper[Any]) -> GetQuestion:
    agent = Agent(
        name="get_question",
        instructions="Generate a question that helps you guess the topic. Be creative and think about the best question to ask.",
        output_type=GetQuestion,
    )
    result = await Runner.run(agent, f"Help me to generate a question that helps me guess the topic. Also, once you are past a dozen question, to makes sense to emit a topic proposal. It is crucial to propose a topic proposal as soon as you are roughly confident about the topic. This is the history of the conversation so far: {ctx.context['messages']}")
    result = GetQuestion.model_validate_json(result.new_items[0].raw_item.content[0].text)
    return f"{result.reasoning}|{result.question}|{result.topic_proposal}"