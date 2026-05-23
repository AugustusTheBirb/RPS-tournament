import inspect
import time
from typing import Any

import numpy as np

import strategies
from strategies import Strategy
from utils import Move, MoveHistory, resolve_moves

if __name__ == "__main__":
    strategy_list: list[Strategy] = [
        obj()
        for name, obj in vars(strategies).items()
        if name != "Strategy" and inspect.isclass(obj) and issubclass(obj, Strategy)
    ]

    print("Strategies:")

    for i, (strategy) in enumerate(strategy_list):
        print(f"{i}: {strategy.name}")

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

    print(f"Selected {strategy_list[index].name}")
    print("To exit enter 'Q'")
    print("To make your move enter 'R'(ock), 'P'(aper) or 'S'(cissors)")

    player_history: MoveHistory = np.empty(1000, dtype=object)
    player_score = 0
    player_move: Move = Move.ROCK  # Initialize to be bounded

    strategy = strategy_list[index]
    strategy_history: MoveHistory = np.empty(1000, dtype=object)
    strategy_context: Any | None = None
    strategy_move: Move

    quit_loop: bool = False
    for i in range(1000):
        while True:
            command: str = input("> ").lower()

            if command == "q":
                quit_loop = True
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

        if quit_loop:
            break

        strategy_move = strategy.make_a_move(strategy_history[:i], player_history[:i])

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
