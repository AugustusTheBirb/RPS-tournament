import argparse
import inspect
import time
from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd
from pandas.core.api import DataFrame

import strategies
from utils import MoveHistory, Strategy, resolve_moves


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
    repeat_count: int, round_count: int, strategy_set: set[Strategy]
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

    game_count: int = len(strategy_set) - 1

    strategy_matchup_scores: dict[tuple[str, str], float] = {}
    strategy_times: dict[str, float] = {
        strategy.__name__[6:]: 0 for strategy in strategy_set
    }

    for strategy_1, strategy_2 in combinations(strategy_set, 2):
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

        strategy_times[strategy_1_name] += total_time_1 / repeat_count / game_count
        strategy_matchup_scores[strategy_1_name, strategy_2_name] = (
            total_score_1 / repeat_count
        )
        strategy_times[strategy_2_name] += total_time_2 / repeat_count / game_count
        strategy_matchup_scores[strategy_2_name, strategy_1_name] = (
            total_score_2 / repeat_count
        )

    df_results: DataFrame = pd.Series(strategy_matchup_scores).unstack()
    df_results["average_score"] = df_results.mean(axis=1)
    df_results = df_results.round(1)
    df_results.sort_values(by="average_score", inplace=True, ascending=False)
    col_order = [c for c in df_results.index] + ["average_score"]
    df_results = df_results[col_order]

    df_times: DataFrame = pd.DataFrame.from_dict(
        strategy_times, columns=["avg_time_ms"], orient="index"
    )

    return df_results, df_times


def plot_results(df_results: pd.DataFrame):
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(12, 6), gridspec_kw={"width_ratios": [3, 1]}
    )

    matrix = df_results.drop(columns="average_score", errors="ignore")
    im = ax1.imshow(matrix.values, cmap="bwr_r", aspect="equal")
    ax1.set_xticks(range(len(matrix.columns)))
    ax1.set_yticks(range(len(matrix.index)))
    ax1.set_xticklabels(matrix.columns, rotation=45, ha="right")
    ax1.set_yticklabels(matrix.index)
    ax1.set_title("Score: row strategy vs column strategy")
    _ = fig.colorbar(im, ax=ax1)

    avg = df_results["average_score"].sort_values()
    ax2.barh(avg.index, avg.values)
    ax2.set_title("Average score")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    strategy_dict: dict[str, Strategy] = {
        name: obj
        for name, obj in inspect.getmembers(strategies, inspect.isfunction)
        if name[:6] == "strat_"
    }
    group_dict: dict[str, list[Strategy]] = {
        name: obj for name, obj in vars(strategies).items() if name[:6] == "group_"
    }
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    _ = parser.add_argument(
        "-g", "--games", help="Number of games to average", type=int, default=3
    )
    _ = parser.add_argument(
        "-r",
        "--rounds",
        help="Number of rounds per game",
        type=int,
        default=1000,
    )
    _ = parser.add_argument("-p", "--plot", help="Draw plot", action="store_true")
    _ = parser.add_argument(
        "-c",
        "--competitors",
        help="list of strategies or strategy groups that compete in the tournament"
        + f"\ngroups: {list(group_dict.keys())}"
        + f"\nstrategies: {list(strategy_dict.keys())}",
        nargs="+",
    )
    args = parser.parse_args()

    round_count: int = args.rounds
    game_count: int = args.games
    print_plot: bool = args.plot

    strategy_set: set[Strategy] = set()

    if args.competitors is not None:
        for competitor_str in args.competitors:
            if competitor_str[:6] == "strat_" and competitor_str in strategy_dict:
                strategy_set.add(strategy_dict[competitor_str])

            elif competitor_str[:6] == "group_" and competitor_str in group_dict:
                for strategy in group_dict[competitor_str]:
                    strategy_set.add(strategy)
    else:
        strategy_set = set(strategy_dict.values())

    df_results, df_times = simulate_tournament(game_count, round_count, strategy_set)

    print(df_times)

    print(f"\nMax points: {round_count}")
    df_results.to_csv("last_run.csv")

    print(df_results)

    if print_plot:
        plot_results(df_results)
