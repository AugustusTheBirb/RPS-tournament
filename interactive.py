import inspect
import time
from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd

import strategies
from utils import Move, MoveHistory, Strategy, move_list_to_str, resolve_moves

# pyright: reportExplicitAny=false


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


def simulate_tournament(
    repeat_count: int, round_count: int, strategy_list: list[Strategy]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Simulates a tournament that includes multiple strategies, each
    strategy is pit against each other (strategies, don't play
    against themselves)

    Args:
        repeat_count: Integer of how many times a game will be repeated
            and awereged out
        round_count: Integer of how many rounds one strategy will
            play against another during a game
        strategy_lis: A list of strategies that will compete
    Returns:
        df_restults: A dataframe of the tournament results
    """

    game_count: int = len(strategy_list) - 1
    strategy_index: pd.Index = pd.Index(list(x.__name__[6:] for x in strategy_list))

    df_results = pd.DataFrame(None, columns=strategy_index, index=strategy_index)
    df_times = pd.DataFrame(
        0, columns=pd.Index(["avg_time_ms"]), index=strategy_index
    ).astype({"avg_time_ms": float})

    for strategy_1, strategy_2 in combinations(strategy_list, 2):
        strategy_1_name: str = strategy_1.__name__[6:]
        total_score_1: int = 0
        total_time_1: float = 0

        strategy_2_name: str = strategy_2.__name__[6:]
        total_score_2: int = 0
        total_time_2: float = 0

        for _ in range(repeat_count):
            (delta_1, time_1), (delta_2, time_2) = simulate_game(
                round_count, strategy_1, strategy_2
            )
            total_score_1 += delta_1
            total_time_1 += time_1
            total_score_2 += delta_2
            total_time_2 += time_2

        df_times.loc[strategy_1_name, "avg_time_ms"] += round(
            total_time_1 / repeat_count / game_count
        ,2)
        df_results.loc[strategy_1_name, strategy_2_name] = round(
            total_score_1 / repeat_count
        )
        df_times.loc[strategy_2_name, "avg_time_ms"] += round(
            total_time_2 / repeat_count / game_count
        ,2)
        df_results.loc[strategy_2_name, strategy_1_name] = round(
            total_score_2 / repeat_count
        )

    df_results["average_score"] = df_results.mean(axis=1)
    df_results = df_results.round(1)
    df_results.sort_values(by="average_score", inplace=True, ascending=False)
    return df_results, df_times


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
        except ValueError as e:
            print("Please enter an integer")

    print(f"Selected {strategy_list[index][0]}")
    print("To exit enter 'Q'")
    print("To make your move enter 'R'(ock), 'P'(aper) or 'S'(cissors)")

    player_history: MoveHistory = np.empty(1000, dtype=object)
    player_score = 0
    player_move: Move

    strategy = strategy_list[index][1]
    strategy_history: MoveHistory = np.empty(1000, dtype=object)
    strategy_context: Any | None = None
    strategy_move: Move


    for i in range(1000):
        command: str = input("> ").lower()

        if command == "q":
            break
        elif command == "r":
            player_move = Move.ROCK
            print("Rock vs. ", end="")
        elif command == "p":
            player_move = Move.PAPER
            print("Paper vs. ", end="")
        elif command == "s":
            player_move = Move.SCISSORS
            print("Scissors vs. ", end="")
        else:
            print("Unknown command")
            continue

        strategy_move, strategy_context = strategy(
            strategy_history[:i], strategy_history[:i], strategy_context
        )

        time.sleep(0.5)
        if(strategy_move == Move.ROCK):
            print("ROCK")
        elif(strategy_move == Move.PAPER):
            print("PAPER")
        elif(strategy_move == Move.SCISSORS):
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
