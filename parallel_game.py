"""
Script for running multiple games of N questions concurrently.
"""

from game import play_game
import fire
import asyncio
import shutil


def play_games(num_games: int = 10, clear_logs: bool = True):
    """
    Play multiple games of 20 questions concurrently.

    :param num_games: The number of games to run concurrently
    :returns: A list of results from all games
    :raises ValueError: If an invalid coroutine is passed
    """

    async def play_game_async():
        """
        Asynchronous wrapper for the play_game function.

        :returns: The result of the play_game function
        """
        return await asyncio.to_thread(play_game)

    async def run_games(num_games: int):
        """
        Run multiple games concurrently.

        :param num_games: The number of games to run
        :returns: A list of results from all games
        """
        tasks = [play_game_async() for _ in range(num_games)]
        return await asyncio.gather(*tasks)

    if clear_logs:
        shutil.rmtree("game_logs")
    results = asyncio.run(run_games(num_games))
    topics = [result[1] for result in results]
    results = [result[0] for result in results]
    wins = sum(1 for result in results if result)
    losses = num_games - wins
    print(f"Games played: {num_games}")
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    print(
        f"Topics guessed correctly: {[topic for topic, result in zip(topics, results) if result]}"
    )
    print(
        f"Topics not guessed: {[topic for topic, result in zip(topics, results) if not result]}"
    )


if __name__ == "__main__":
    fire.Fire(play_games)
