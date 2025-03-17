import fire
from custom_agents import HostAgent, GuesserAgent
from agents import Runner
from messages import round_message
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
    logger.info(f"Let's play the game of {max_num_rounds} questions!")
    host_agent = HostAgent(topic=topic, logger=logger)
    guesser_agent = GuesserAgent(logger=logger)
    # add trace
    # add guardrails # final_output = result.final_output_as(HomeworkOutput)
    # handoffs=[history_tutor_agent, math_tutor_agent],
    # proper loop
    for step in range(max_num_rounds):
        logger.info("----------------------------------------")
        logger.info(f"Step {step} of the game")

        # # inform both agents about the current step
        # # not very important for the Host,
        # # but super important for the Guesser
        host_agent.messages.append({"role": "user", "content": round_message.format(round_number=step, max_num_rounds=max_num_rounds)})
        guesser_agent.messages.append({"role": "user", "content": round_message.format(round_number=step, max_num_rounds=max_num_rounds)})

        # Guesser actions
        question, topic_proposal = guesser_agent.generate_question()
        if topic_proposal is not None:
            # Host optionally validates the topic proposal
            is_correct = host_agent.validate_topic_proposal(topic_proposal)
            if is_correct:
                return True, host_agent.topic

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
