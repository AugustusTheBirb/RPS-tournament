import inspect
import time
from typing import Any

import numpy as np

import strategies
from utils import Move, MoveHistory, Strategy, resolve_moves


def simulate_game(
    round_count: int, strategy_1: Strategy, strategy_2: Strategy
) -> tuple[tuple[int, float], tuple[int, float]]:
    """
    Simulates a game - a set of multiple rounds, scores of both
    players are retured as a result

    Args:
        round_count: An integer indicating how many rounds will be played
    Returns:
        strategy_1_score: An integer of how many points were scored by
            the first player
        strategy_2_score: An integer of how many points were scored by
            the second player
    """
    strategy_1_history: MoveHistory = np.empty(round_count, dtype=object)
    strategy_1_score = 0
    strategy_1_time_ms: float = 0
    context_1: Any | None = None

    strategy_2_history: MoveHistory = np.empty(round_count, dtype=object)
    strategy_2_score = 0
    strategy_2_time_ms: float = 0
    context_2: Any | None = None

    for i in range(round_count):
        start_time = time.time()
        move_1, context_1 = strategy_1(
            strategy_1_history[:i], strategy_2_history[:i], context_1
        )
        end_time = time.time()
        strategy_1_time_ms += (end_time - start_time) * 1000

        start_time = time.time()
        move_2, context_2 = strategy_2(
            strategy_2_history[:i], strategy_1_history[:i], context_2
        )
        end_time = time.time()
        strategy_2_time_ms += (end_time - start_time) * 1000

        delta_1, delta_2 = resolve_moves(move_1, move_2)

        strategy_1_score += delta_1
        strategy_1_history[i] = move_1

        strategy_2_score += delta_2
        strategy_2_history[i] = move_2

    return (strategy_1_score, strategy_1_time_ms), (
        strategy_2_score,
        strategy_2_time_ms,
    )


if __name__ == "__main__":
    strategy_list: list[tuple[str, Strategy]] = [
        (name[6:], obj)
        for name, obj in inspect.getmembers(strategies, inspect.isfunction)
        if name[:6] == "strat_"
    ]

    print("Strategies:")

    for i, (name, _) in enumerate(strategy_list):
        print(f"{i}: {name}")

    retry: bool = True
    index: int = 0
    while retry:
        try:
            index = int(input("Which strategy would you like to play against > "))

            if index < 0:
                print("Please enter an integer bigger than 0")
                continue
            if len(strategy_list) <= index:
                print(f"Please enter an integer smaller than {len(strategy_list)}")
                continue

            retry = False
        except ValueError:
            print("Please enter an integer")

    print(f"Selected {strategy_list[index][0]}")
    print("To exit enter 'Q'")
    print("To make your move enter 'R'(ock), 'P'(aper) or 'S'(cissors)")

    player_history: MoveHistory = np.empty(1000, dtype=object)
    player_score = 0
    player_move: Move = Move.ROCK  # Initialize to be bounded

    strategy = strategy_list[index][1]
    strategy_history: MoveHistory = np.empty(1000, dtype=object)
    strategy_context: Any | None = None
    strategy_move: Move

    quit: bool = False
    for i in range(1000):
        while True:
            command: str = input("> ").lower()

            if command == "q":
                quit = True
                break
            elif command == "r":
                player_move = Move.ROCK
                print("Rock vs. ", end="")
                break
            elif command == "p":
                player_move = Move.PAPER

                break
            elif command == "s":
                player_move = Move.SCISSORS
                print("Scissors vs. ", end="")
                break
            else:
                print("Unknown command")
                continue

        if quit:
            break

        strategy_move, strategy_context = strategy(
            strategy_history[:i], player_history[:i], strategy_context
        )

        time.sleep(0.5)
        if strategy_move == Move.ROCK:
            print("ROCK")
        elif strategy_move == Move.PAPER:
            print("PAPER")
        elif strategy_move == Move.SCISSORS:
            print("SCISSORS")

        player_history[i] = player_move
        strategy_history[i] = strategy_move

        delta, _ = resolve_moves(player_move, strategy_move)
        player_score += delta

        if 0 < delta:
            print(f"You won! Your score is now: {player_score}")

        elif delta < 0:
            print(f"You lost... Your score is now: {player_score}")

        else:
            print(f"Tie. Your score is now: {player_score}")
