"""Module that lets the user run the RPS tournament."""

import argparse
import inspect

import strategies
from strategies import Strategy
from tournament import plot_results, simulate_tournament

if __name__ == "__main__":
    strategy_dict: dict[str, Strategy] = {
        name: obj()
        for name, obj in vars(strategies).items()
        if inspect.isclass(obj)
        and not inspect.isabstract(obj)
        and issubclass(obj, Strategy)
    }
    group_dict: dict[str, list[Strategy]] = {
        name: obj for name, obj in vars(strategies).items() if name[:6] == "group_"
    }

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    _ = parser.add_argument(
        "-g",
        "--games",
        help="Number of games to average",
        type=int,
        default=3,
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
        f"\ngroups: {list(group_dict.keys())}"
        f"\nstrategies: {list(strategy_dict.keys())}",
        nargs="+",
    )
    args = parser.parse_args()

    round_count: int = args.rounds
    game_count: int = args.games
    print_plot: bool = args.plot

    strategy_set: set[Strategy] = set()

    if args.competitors is not None:
        for competitor_str in args.competitors:
            if competitor_str in strategy_dict:
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
