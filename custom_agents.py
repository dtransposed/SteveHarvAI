import json
import logging
import time
import random
from typing import Dict, Any, Tuple, Optional
from agents import Agent, Runner, MessageOutputItem
from tools import (
    generate_topic_agent,
    get_question_agent,
    get_answer_agent,
    validate_topic_proposal_agent,
)
from messages import topic_message
from prompts import SYSTEM_PROMPT_HOST, SYSTEM_PROMPT_GUESSER
import uuid
from config import model_type_host, model_type_guesser


class BaseGameAgent(Agent):
    """
    Base class for game agents with common functionality.

    :param name: Name of the agent
    :param system_prompt: System prompt for the agent
    :param model: Model to use for this agent
    :param handoffs: List of agents this agent can hand off to
    :param logger: Logger instance to use
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        model: str | None,
        handoffs: list = None,
        logger: logging.Logger | None = None,
    ):
        super().__init__(
            name=name, instructions=system_prompt, model=model, handoffs=handoffs or []
        )
        self.messages = []
        self.logger = logger or logging.getLogger()

    def _run_agent_and_extract_response(
        self, message: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Run the agent with a message and extract the response.

        :param message: Message to send to the agent
        :param context: Optional context to pass to the agent
        :returns: Parsed JSON response
        """
        for attempt in range(3):
            try:
                self.messages.append({"role": "user", "content": message})
                result = Runner.run_sync(self, self.messages, context=context)
                self.messages = result.to_input_list()

                # Extract the message content
                message_output_item = next(
                    item
                    for item in result.new_items
                    if isinstance(item, MessageOutputItem)
                )
                content = message_output_item.raw_item.content[0].text

                parsed_response = json.loads(content)
                return parsed_response

            except Exception as e:
                breakpoint()
                self.logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt == 2:  # Last attempt
                    raise e

    def _log_internal_dialogue(self, reasoning: str, prefix: str = "internal dialogue"):
        """
        Log the agent's internal dialogue.

        :param reasoning: Reasoning text to log
        :param prefix: Optional prefix for the log message
        """
        self.logger.info(f"{self.name} ({prefix}): {reasoning}")


class HostAgent(BaseGameAgent):
    """
    Host agent for the 20 questions game. Generates topics and validates guesses.

    :param system_prompt: System prompt for the agent
    :param model: Model to use for this agent
    :param topic: Optional predefined topic for the game
    :param logger: Logger instance to use
    """

    def __init__(
        self,
        system_prompt: str = SYSTEM_PROMPT_HOST,
        model: str | None = model_type_host,
        topic: str | None = None,
        logger: logging.Logger | None = None,
    ):
        super().__init__(
            name="Host",
            system_prompt=system_prompt,
            model=model,
            handoffs=[
                generate_topic_agent,
                get_answer_agent,
                validate_topic_proposal_agent,
            ],
            logger=logger,
        )
        if topic is None:
            self.topic = self._generate_topic()
        else:
            self.messages.append(
                {
                    "role": "user",
                    "content": f"IMPORTANT: The topic for this game is: {topic}",
                }
            )
            self.topic = topic

    def _generate_topic(self) -> str:
        """
        Generate a new topic for the game.

        :returns: Generated topic string
        """
        response = self._run_agent_and_extract_response(
            topic_message.format(unique_id=uuid.uuid4())
        )

        self._log_internal_dialogue(
            f"Generated topic: {response['topic']} from category: {response['category']}/{response['sub_category']}. "
            f"Reasoning: {response['reasoning']}"
        )
        return response["topic"]

    def generate_answer(self, question: str) -> Tuple[str, str]:
        """
        Generate an answer to the question.

        :param question: Question to answer
        :returns: Tuple of (answer, reasoning)
        """
        response = self._run_agent_and_extract_response(
            f"Use the 'get_answer' agent to generate an answer to the question: {question}."
        )

        reasoning, answer = response["reasoning"], response["answer"]
        self._log_internal_dialogue(reasoning)
        return answer

    def validate_topic_proposal(self, topic_proposal: str) -> bool:
        """
        Validate the topic proposal.

        :param topic_proposal: Proposed topic to validate
        :returns: True if the proposal is correct, False otherwise
        """
        response = self._run_agent_and_extract_response(
            "Use the 'validate_topic_proposal' agent to validate the topic proposal.",
            context={"topic_proposal": topic_proposal, "topic": self.topic},
        )
        reasoning, is_correct = response["reasoning"], response["is_correct"]
        self._log_internal_dialogue(reasoning)
        return is_correct


class GuesserAgent(BaseGameAgent):
    """
    Guesser agent for the 20 questions game. Generates questions and guesses the topic.

    :param system_prompt: System prompt for the agent
    :param model: Model to use for this agent
    :param logger: Logger instance to use
    """

    def __init__(
        self,
        system_prompt: str = SYSTEM_PROMPT_GUESSER,
        model: str | None = model_type_guesser,
        logger: logging.Logger | None = None,
    ):
        super().__init__(
            name="Guesser",
            system_prompt=system_prompt,
            model=model,
            handoffs=[get_question_agent],
            logger=logger,
        )

    def generate_question(self) -> Tuple[str, Optional[str]]:
        """
        Generate a question about the topic.

        :returns: Tuple of (question, topic_proposal) where topic_proposal may be None
        """
        response = self._run_agent_and_extract_response(
            "Use the appropriate agent to generate a question about the topic."
        )
        time.sleep(random.randint(1, 5))

        question = response["question"]
        reasoning = response["reasoning"]
        topic_proposal = response["topic_proposal"]

        self._log_internal_dialogue(reasoning)

        if topic_proposal is not None:
            self._log_internal_dialogue(f"I proposed the topic: {topic_proposal}")

        return question, topic_proposal

    def acknowledge_answer(self, question: str, answer: str):
        """
        Acknowledge the answer to a question.

        :param question: The question that was asked
        :param answer: The answer to the question
        """
        self.messages.append(
            {
                "role": "user",
                "content": f"The answer to the question: {question} is: {answer}",
            }
        )

    def acknowledge_bad_topic_proposal(self, topic_proposal: str):
        self.messages.append(
            {
                "role": "user",
                "content": f"The topic {topic_proposal} is not correct. Try again.",
            }
        )
