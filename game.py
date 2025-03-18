import fire
from custom_agents import HostAgent, GuesserAgent
from messages import round_message
import uuid
from agents import trace
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
    logger.info(f"Let's play the game of {max_num_rounds} questions!")
    host_agent = HostAgent(topic=topic, logger=logger)
    guesser_agent = GuesserAgent(logger=logger)

    with trace(f"game-{game_id}"):
        for step in range(max_num_rounds):
            logger.info("----------------------------------------")
            logger.info(f"Step {step} of the game")

            guesser_agent.messages.append(
                {
                    "role": "user",
                    "content": round_message.format(
                        round_number=step, max_num_rounds=max_num_rounds
                    ),
                }
            )
            question, topic_proposal = guesser_agent.generate_question()
            if topic_proposal is not None:
                # Host optionally validates the topic proposal
                is_correct = host_agent.validate_topic_proposal(topic_proposal)
                if is_correct:
                    logger.info(f"Guesser wins! The topic is {host_agent.topic}")
                    return True, host_agent.topic
                else:
                    logger.info(f"Host: {topic_proposal} is not correct. Try again.")
                    guesser_agent.acknowledge_bad_topic_proposal(topic_proposal)

            logger.info(f"Guesser: {question}")

            # Host actions
            answer = host_agent.generate_answer(question)
            logger.info(f"Host: {answer}")
            guesser_agent.acknowledge_answer(question, answer)

        logger.info(
            f"The Guesser has not guessed the topic in {step + 1} steps. The Guesser loses!"
        )
        return False, host_agent.topic


if __name__ == "__main__":
    fire.Fire(play_game)
