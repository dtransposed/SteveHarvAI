import json
import logging
from agents import Agent, Runner, MessageOutputItem, ToolCallOutputItem, ToolCallItem
from tools import (
        get_topic_tool, get_question_tool, get_answer_tool, get_validate_topic_proposal_tool
)
from messages import topic_message, question_message
from prompts import SYSTEM_PROMPT_HOST, SYSTEM_PROMPT_GUESSER
import uuid


class HostAgent(Agent):
    def __init__(
        self,
        system_prompt: str = SYSTEM_PROMPT_HOST,
        model: str | None = "gpt-4o-mini",
        topic: str | None = None,
        logger: logging.Logger | None = None,
    ):
        """
        Initialize the Host agent.
        
        :param system_prompt: System prompt for the agent
        :param model: Model to use for this agent
        :param topic: Topic for the game, if None one will be generated
        :param logger: Logger instance to use
        """
        super().__init__(
            name="Host", 
            instructions=system_prompt, 
            model=model, 
            tools=[get_topic_tool, get_answer_tool, get_validate_topic_proposal_tool]
        )
        self.messages = []
        self.logger = logger or logging.getLogger()
        self.topic = topic or self._generate_topic()
        
    def _generate_topic(self) -> str:
        """
        Generate a new topic for the game.
        """
        self.messages.append({"role": "user", "content": topic_message.format(unique_id=uuid.uuid4())})
        result = Runner.run_sync(self, self.messages)
        self.messages = result.to_input_list()
        tool_call_output_item = next(item for item in result.new_items if isinstance(item, ToolCallOutputItem))
        response = json.loads(tool_call_output_item.output)
        self.logger.info(
            f"Host (internal dialogue): Generated topic: {response['topic']} from category: {response['category']}/{response['sub_category']}. Reasoning: {response['reasoning']}"
        )
        return response['topic']

    def generate_answer(self, question: str) -> tuple[str, str]:
        """
        Generate an answer to the question.
        """
        # Create a message that explicitly instructs the model to use the topic from context
        self.messages.append({"role": "user", "content": f"Use the appropriate tool to generate an answer to the question."})
        result = Runner.run_sync(self, self.messages, context={"question": question, "topic": self.topic})
        self.messages = result.to_input_list()
        new_messages = result.new_items
        tool_call_output_items = [item for item in new_messages if isinstance(item, ToolCallOutputItem)]
        assert len(tool_call_output_items) == 1, "Expected exactly one ToolCallOutputItem (get_answer)"
        reasoning = tool_call_output_items[0].output.split("|")[0]
        answer = tool_call_output_items[0].output.split("|")[1]
        self.logger.info(f"Host (internal dialogue): {reasoning}")
        return answer

    def validate_topic_proposal(self, topic_proposal: str) -> tuple[str, str]:
        """
        Validate the topic proposal.
        """
        self.messages.append({"role": "user", "content": f"Use the appropriate tool to validate the topic proposal."})
        result = Runner.run_sync(self, self.messages, context={"topic_proposal": topic_proposal, "topic": self.topic})
        self.messages = result.to_input_list()
        new_messages = result.new_items
        tool_call_output_items = [item for item in new_messages if isinstance(item, ToolCallOutputItem)]
        assert len(tool_call_output_items) == 1, "Expected exactly one ToolCallOutputItem (get_validate_topic_proposal)"
        reasoning = tool_call_output_items[0].output.split("|")[0]
        is_correct = tool_call_output_items[0].output.split("|")[1]
        breakpoint()
        self.logger.info(f"Host (internal dialogue): {reasoning}")
        return is_correct


class GuesserAgent(Agent):
    def __init__(
        self, 
        system_prompt: str = SYSTEM_PROMPT_GUESSER, 
        model: str | None = "gpt-4o-mini",
        logger: logging.Logger | None = None,
    ):
        """
        Initialize the Guesser agent.
        
        :param system_prompt: System prompt for the agent
        :param model: Model to use for this agent
        :param logger: Logger instance to use
        """
        super().__init__(
            name="Guesser",
            instructions=system_prompt, 
            model= model,
            tools=[get_question_tool]
        )
        self.messages = []
        self.logger = logger or logging.getLogger()

    def generate_question(self) -> str:
        """
        Generate a question about the topic.
        """

        self.messages.append({"role": "user", "content": "Use the appropriate tool to generate a question about the topic."})
        result = Runner.run_sync(self, self.messages, context={"messages": self.messages})
        self.messages = result.to_input_list()
        new_messages = result.new_items
        tool_call_output_items = [item for item in new_messages if isinstance(item, ToolCallOutputItem)]
        assert len(tool_call_output_items) == 1, "Expected exactly one ToolCallOutputItem (get_validate_topic_proposal)"
        reasoning = tool_call_output_items[0].output.split("|")[0]
        question = tool_call_output_items[0].output.split("|")[1]
        topic_proposal = tool_call_output_items[0].output.split("|")[2]
        self.logger.info(f"Guesser (internal dialogue): {reasoning}")
        if topic_proposal != 'None':
            breakpoint()
        topic_proposal = None if topic_proposal == 'None' else topic_proposal
        if topic_proposal is not None:
            self.logger.info(f"Guesser (internal dialogue): I proposed the topic: {topic_proposal}")

        return question, topic_proposal
    
    def acknowledge_answer(self, question: str, answer: str):
        """
        Acknowledge the answer.
        """
        self.messages.append({"role": "user", "content": f"The answer to the question: {question} is: {answer}"})
