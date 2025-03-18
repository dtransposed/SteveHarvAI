"""
Simplified script for running multiple games of N questions concurrently using multiprocessing.
"""

from game import play_game
import fire
import multiprocessing
import os
import time
import shutil


def run_game_safely(game_id):
    """
    Run a single game with error handling.

    :param game_id: ID of the game for logging purposes
    :returns: The result of the game or None if an error occurred
    """
    try:
        return play_game(), None
    except Exception as e:
        return None, f"Game {game_id} failed: {str(e)}"


def play_games(
    num_games: int = 5,
    clear_logs: bool = True,
    max_concurrent: int = None,
    show_progress: bool = True,
):
    """
    Play multiple games concurrently using multiprocessing.

    :param num_games: The number of games to run in total
    :param clear_logs: Whether to clear logs before starting
    :param max_concurrent: Maximum processes to run concurrently (defaults to CPU count)
    :param show_progress: Whether to show basic progress updates
    :returns: A list of results from successful games
    """
    start_time = time.time()

    # Clear logs if requested
    if clear_logs:
        try:
            shutil.rmtree("game_logs")
        except FileNotFoundError:
            pass
        os.makedirs("game_logs", exist_ok=True)

    # Create a pool of workers
    max_concurrent = (
        multiprocessing.cpu_count() if max_concurrent is None else max_concurrent
    )
    with multiprocessing.Pool(processes=max_concurrent) as pool:
        # Submit all tasks to the pool with game IDs
        async_results = [
            pool.apply_async(run_game_safely, (i,)) for i in range(num_games)
        ]

        # Track progress
        completed = 0
        results = []
        errors = []

        # Wait for all processes to complete
        for async_result in async_results:
            try:
                # Get the result (blocks until available)
                result, error = async_result.get()

                if error:
                    errors.append(error)
                elif result is not None:
                    results.append(result)

                # Update progress
                completed += 1
                if show_progress:
                    print(
                        f"Progress: {completed}/{num_games} games ({completed / num_games * 100:.1f}%)"
                    )
            except Exception as e:
                errors.append(f"Error getting result: {str(e)}")

    # Basic stats
    total_time = time.time() - start_time
    successful_games = len(results)
    games_won = sum(1 for win, _ in results if win)

    print("\n========== RESULTS ==========")
    print(f"Games played: {num_games} in {total_time:.2f} seconds")
    print(f"Games won: {games_won}")
    print(f"Win rate: {games_won / successful_games * 100:.1f}%")
    print(f"Failed games: {len(errors)}")

    if errors:
        print("\nErrors encountered:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"- {error}")
        if len(errors) > 5:
            print(f"... and {len(errors) - 5} more errors")

    if successful_games > 0:
        wins = sum(1 for win, _ in results if win)
        print(f"\nWin rate: {wins / successful_games * 100:.1f}%")

    return results


if __name__ == "__main__":
    fire.Fire(play_games)
