import logging
from openai import OpenAI
from tools import GetTopic, GetQuestion, GetAnswer, ValidateAnswer
from messages import AssistantMessage, UserMessage, StepMessage, SystemMessage
from pydantic import BaseModel
from prompts import SYSTEM_PROMPT_HOST, SYSTEM_PROMPT_GUESSER
import uuid
import random


class Agent:
    def __init__(
        self,
        system_prompt: str,
        model: str | None = None,
        default_model: str = "gpt-4o-mini",
    ):
        """
        Initialize the agent.

        :param system_prompt: The system prompt for the agent.
        :param model: The model to use for the agent.
            Optional, if we'd like to use the specific model for the agent.
        :param default_model: The default model to use for the agent.
        """
        self.client = OpenAI()
        self.model = model or default_model
        self.system_prompt = system_prompt
        self.messages = [SystemMessage(content=system_prompt)]

    def add_message(self, message: BaseModel):
        # Add the message to the memory
        self.messages.append(message)

    def convert_messages_to_openai_format(self) -> list[dict[str, str]]:
        # Convert the messages to the OpenAI format for the LLM call
        messages_formatted = []
        for message in self.messages:
            if isinstance(message, (UserMessage, AssistantMessage, SystemMessage)):
                messages_formatted.append(
                    {"role": message.role, "content": message.content}
                )
            elif isinstance(message, StepMessage):
                messages_formatted.append(
                    {"role": "user", "content": f"Current step: {message.step}"}
                )
            else:
                raise ValueError(f"Unknown message type: {type(message)}")
        return messages_formatted

    def llm_call(
        self,
        response_format: BaseModel,
        prompt: str,
        temperature: float = 0.0,
        n: int = 1,
    ) -> BaseModel:
        messages_formatted = self.convert_messages_to_openai_format()
        messages_formatted.append({"role": "user", "content": prompt})
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=messages_formatted,
            response_format=response_format,
            temperature=temperature,
            n=n,
        )
        if n > 1:
            return random.choice(response.choices).message.parsed

        return response.choices[0].message.parsed


class HostAgent(Agent):
    def __init__(
        self,
        system_prompt: str = SYSTEM_PROMPT_HOST,
        model: str | None = None,
        topic: str | None = None,
    ):
        """
        Initialize the Host agent.
        """
        super().__init__(system_prompt=system_prompt, model=model)

        if topic is None:
            logging.info("No topic provided, generating a new one...")
            topic = self.generate_topic()
        self.topic = topic
        self.add_message(
            AssistantMessage(content=f"The topic of the game is: {topic}.")
        )

    def generate_topic(self) -> str:
        """
        Generate a new topic for the game.
        """
        unique_id = uuid.uuid4()
        prompt = (
            f"Provide a unique and random topic for a game of 20 questions. "
            f"Here is a unique seed to ensure randomness and diversity: '{unique_id}'. "
            f"Ensure the topic is diverse, creative, and comes from a broad range of categories. "
        )

        response = self.llm_call(GetTopic, prompt, temperature=0.99, n=10)
        logging.debug(
            f"Generated topic: {response.topic} from category: {response.category}/{response.sub_category}. Reasoning: {response.reasoning}"
        )
        return response.topic

    def generate_answer(self) -> tuple[str, str]:
        """
        Generate an answer to the question.
        """
        response = self.llm_call(
            GetAnswer,
            f"Please answer the most recent question for the topic: {self.topic}. Explain your answer.",
        )
        # Add the "internal thought" to the memory
        self.add_message(
            AssistantMessage(
                content="My reasoning: "
                + response.reasoning
                + "\n\nI answered: "
                + response.answer
            )
        )
        return response.reasoning, response.answer

    def validate_topic_proposal(self, topic_proposal: str) -> tuple[str, str]:
        """
        Validate the topic proposal.
        """
        response = self.llm_call(
            ValidateAnswer,
            f"The Guesser has proposed the topic: {topic_proposal}. Did the Guesser guess the topic: {self.topic}?",
        )
        return response.reasoning, response.is_correct


class GuesserAgent(Agent):
    def __init__(
        self, system_prompt: str = SYSTEM_PROMPT_GUESSER, model: str | None = None
    ):
        """
        Initialize the Guesser agent.
        """
        super().__init__(system_prompt=system_prompt, model=model)

    def generate_question(self) -> str:
        """
        Generate a question about the topic.
        """
        response = self.llm_call(
            GetQuestion,
            "Generate a question that helps you guess the topic. Be creative and think about the best question to ask.",
        )
        # Add the "internal thought" to the memory
        content = f"My reasoning: {response.reasoning}\n\nI asked the question: {response.question}"
        if response.topic_proposal is not None:
            content += f"\n\nI proposed the topic: {response.topic_proposal}"
        self.add_message(AssistantMessage(content=content))
        return response.reasoning, response.question, response.topic_proposal
