"""Module that implements the main tournament functionality."""

import os
import time
from collections import defaultdict
from copy import deepcopy
from itertools import combinations
from multiprocessing import Pool
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from pandas.core.api import DataFrame

    from strategies import Strategy

from utils import MoveHistory, move_list_to_str, resolve_moves


def simulate_game(
    round_count: int,
    strategy_1: Strategy,
    strategy_2: Strategy,
    *,
    verbose: bool = False,
    plot: bool = False,
) -> tuple[tuple[Strategy, int, float], tuple[Strategy, int, float]]:
    """
    Simulate a game - a set of multiple rounds.

    Args:
        round_count: An integer indicating how many rounds will be played.
        strategy_1: First compedint RPS strategy.
        strategy_2: Second compedint RPS strategy.
        verbose: Bool if to print all strategy moves.
        plot: Bool if to plot a graph of strategy scores.

    Returns:
        strategy_1_score: An integer of how many points were scored by
            the first player.
        strategy_2_score: An integer of how many points were scored by
            the second player.

    """
    score_1_per_round = np.empty(round_count, dtype=int)
    score_2_per_round = np.empty(round_count, dtype=int)

    strategy_1_history: MoveHistory = np.empty(round_count, dtype=object)
    strategy_1_score = 0
    strategy_1_time_ms: float = 0

    strategy_2_history: MoveHistory = np.empty(round_count, dtype=object)
    strategy_2_score = 0
    strategy_2_time_ms: float = 0

    for i in range(round_count):
        start_time = time.time()
        move_1 = strategy_1.make_a_move(strategy_1_history[:i], strategy_2_history[:i])
        end_time = time.time()
        strategy_1_time_ms += (end_time - start_time) * 1000

        start_time = time.time()
        move_2 = strategy_2.make_a_move(strategy_2_history[:i], strategy_1_history[:i])
        end_time = time.time()
        strategy_2_time_ms += (end_time - start_time) * 1000

        delta_1, delta_2 = resolve_moves(move_1, move_2)

        strategy_1_score += delta_1
        strategy_1_history[i] = move_1

        strategy_2_score += delta_2
        strategy_2_history[i] = move_2

        if plot:
            score_1_per_round[i] = strategy_1_score
            score_2_per_round[i] = strategy_2_score

    if verbose:
        print(
            f"{strategy_1.name.ljust(20)}: "
            f"{move_list_to_str(list(strategy_1_history))}",
        )
        print(
            f"{strategy_2.name.ljust(20)}: "
            f"{move_list_to_str(list(strategy_2_history))}",
        )

    if plot:
        rounds = np.arange(1, round_count + 1)
        _ = plt.plot(rounds, score_1_per_round, label=strategy_1.name)
        _ = plt.plot(rounds, score_2_per_round, label=strategy_2.name)
        _ = plt.xlabel("Round")
        _ = plt.ylabel("Cumulative score")
        _ = plt.legend()
        _ = plt.show()

    return (strategy_1, strategy_1_score, strategy_1_time_ms), (
        strategy_2,
        strategy_2_score,
        strategy_2_time_ms,
    )


def simulate_tournament(
    repeat_count: int,
    round_count: int,
    strategy_set: set[Strategy],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Simulate a tournament that includes multiple strategies, each
    strategy is pit against each other (strategies, don't play
    against themselves).

    Args:
        repeat_count: Integer of how many times a game will be repeated
            and awereged out.
        round_count: Integer of how many rounds one strategy will
            play against another during a game.
        strategy_set: A set of strategies that will compete.

    Returns:
        df_restults: A dataframe of the tournament results.

    """
    game_count: int = len(strategy_set) - 1

    strategy_matchup_scores: defaultdict[tuple[str, str], float] = defaultdict(float)
    strategy_times: defaultdict[str, float] = defaultdict(float)

    strategy_pairs = combinations(strategy_set, 2)
    argument_list = [(round_count, *strategy_pair) for strategy_pair in strategy_pairs]
    # Copy strategy object, so they do not interfere with eachother
    argument_list = [
        (round_count, deepcopy(strat_1), deepcopy(strat_2))
        for (round_count, strat_1, strat_2) in argument_list
        for _ in range(repeat_count)
    ]

    with Pool(processes=os.cpu_count()) as pool:
        results = pool.starmap(simulate_game, argument_list)

    for (strategy_1, score_1, time_1), (strategy_2, score_2, time_2) in results:
        strategy_matchup_scores[strategy_1.name, strategy_2.name] += (
            score_1 / repeat_count
        )
        strategy_times[strategy_1.name] += time_1 / repeat_count / game_count

        strategy_matchup_scores[strategy_2.name, strategy_1.name] += (
            score_2 / repeat_count
        )
        strategy_times[strategy_2.name] += time_2 / repeat_count / game_count

    df_results: DataFrame = (
        pd.Series(strategy_matchup_scores, name="scores")
        .rename_axis(index=["strategy", "opponent"])
        .reset_index()
        .pivot_table(index="strategy", columns="opponent", values="scores")
    )
    df_results["average_score"] = df_results.mean(axis=1)
    df_results = df_results.round(1)
    df_results = df_results.sort_values(by="average_score", ascending=False)
    col_order = [*df_results.index, "average_score"]
    df_results = df_results[col_order]

    df_times: DataFrame = pd.DataFrame.from_dict(
        strategy_times,
        columns=["avg_time_ms"],
        orient="index",
    )

    return df_results, df_times


def plot_results(df_results: pd.DataFrame) -> None:
    """
    Plot results of a tournament.

    Args:
        df_results: 2d sheet of all competitor scores against each other.

    """
    fig, (ax1, ax2) = plt.subplots(
        1,
        2,
        figsize=(12, 6),
        gridspec_kw={"width_ratios": [3, 1]},
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
