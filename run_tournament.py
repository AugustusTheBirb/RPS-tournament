import inspect
from itertools import combinations

import numpy as np
import pandas as pd

import strategies
from utils import MoveHistory, Strategy, resolve_moves


def simulate_game(
    round_count: int, strategy_1: Strategy, strategy_2: Strategy
) -> tuple[int, int]:
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

    strategy_2_history: MoveHistory = np.empty(round_count, dtype=object)
    strategy_2_score = 0

    for i in range(round_count):
        move_1 = strategy_1(strategy_1_history[:i], strategy_2_history[:i])
        move_2 = strategy_2(strategy_2_history[:i], strategy_1_history[:i])

        delta_1, delta_2 = resolve_moves(move_1, move_2)

        strategy_1_score += delta_1
        strategy_1_history[i] = move_1

        strategy_2_score += delta_2
        strategy_2_history[i] = move_2

    return strategy_1_score, strategy_2_score


def simulate_tournament(
    repeat_count: int, round_count: int, strategy_list: list[Strategy]
) -> pd.DataFrame:
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

    strategy_index: pd.Index = pd.Index(list(x.__name__ for x in strategy_list))

    df_results = pd.DataFrame(0, columns=strategy_index, index=strategy_index)

    for strategy_1, strategy_2 in combinations(strategy_list, 2):
        strategy_1_name: str = strategy_1.__name__
        total_score_1: int = 0

        strategy_2_name: str = strategy_2.__name__
        total_score_2: int = 0

        for _ in range(repeat_count):
            delta_1, delta_2 = simulate_game(round_count, strategy_1, strategy_2)
            total_score_1 += delta_1
            total_score_2 += delta_2

        df_results.loc[strategy_1_name, strategy_2_name] = round(
            total_score_1 / repeat_count
        )
        df_results.loc[strategy_2_name, strategy_1_name] = round(
            total_score_2 / repeat_count
        )

    df_results["average_score"] = df_results.mean(axis=1)
    df_results = df_results.round(1)

    return df_results


if __name__ == "__main__":
    strategy_list = [
        obj for _, obj in inspect.getmembers(strategies, inspect.isfunction)
    ]

    round_count = 1000
    df_results: pd.DataFrame = simulate_tournament(3, round_count, strategy_list)

    print(f"Max points: {round_count}")
    df_results.to_csv("last_run.csv")

    print(df_results)
