import fire
from agents import HostAgent, GuesserAgent
from messages import StepMessage, UserMessage
import uuid
from utils import setup_logger


def play_game(
    topic: str | None = None, max_num_rounds: int = 20, game_id: uuid.UUID | None = None
) -> tuple[bool, str]:
    """
    Play the game of 20 questions.

    :param topic: The topic to be guessed. If not provided, a topic will be generated.
    :param max_num_rounds: The maximum number of rounds to play. Default is 20.
    :param game_id: Unique identifier for the game instance. If None, a new UUID is generated.
    :return: Tuple containing a boolean indicating if the Guesser wins and the topic.
    """
    if game_id is None:
        game_id = uuid.uuid4()

    logger = setup_logger(game_id)
    host_agent = HostAgent(topic=topic)
    guesser_agent = GuesserAgent()
    for step in range(max_num_rounds):
        if step == 0:
            logger.info(f"Let's play the game of {max_num_rounds} questions!")
            logger.info(
                f"Host: Psst...The Guesser doesn't know this, but I can reveal that the topic is {host_agent.topic}"
            )

        logger.info("----------------------------------------")
        logger.info(f"Step {step} of the game")

        # inform both agents about the current step
        # not very important for the Host,
        # but super important for the Guesser
        step_message = StepMessage(step=step)
        host_agent.add_message(step_message)
        guesser_agent.add_message(step_message)

        # Guesser actions
        reasoning, question, topic_proposal = guesser_agent.generate_question()
        logger.info(f"Guesser (internal dialogue): {reasoning}")
        logger.info(f"Guesser: (topic proposal): {topic_proposal}")

        if topic_proposal is not None:
            # Host optionally validates the topic proposal
            reasoning, is_correct = host_agent.validate_topic_proposal(topic_proposal)
            logger.info(f"Host (internal dialogue on topic proposal): {reasoning}")
            if is_correct:
                logger.info(
                    f"Host: Yes, that's correct! The Guesser's topic proposal: {topic_proposal} matches the topic: {host_agent.topic}"
                )
                return True, host_agent.topic

        logger.info(f"Guesser: {question}")
        # communication Guesser -> Host
        host_agent.add_message(UserMessage(content=f"Guesser: {question}"))

        # Host actions
        reasoning, answer = host_agent.generate_answer()
        logger.info(f"Host (internal dialogue): {reasoning}")
        logger.info(f"Host: {answer}")
        # communication Host -> Guesser
        guesser_agent.add_message(UserMessage(content=f"Host: {answer}"))

    logger.info(
        f"The Guesser has not guessed the topic in {step + 1} steps. The Guesser loses!"
    )
    return False, host_agent.topic


if __name__ == "__main__":
    fire.Fire(play_game)
