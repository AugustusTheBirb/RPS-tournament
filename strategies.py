import random
from collections import Counter
from typing import Any

from utils import Move, MoveHistory, get_counter

# pyright: reportUnusedParameter=false, reportExplicitAny=false

"""
Args:
    my_moves: A history of this strategy moves this game
    opponent_moves: A history of opponent strategy moves this game
Returns:
    A move this strategy will make next
"""


def strat_beats_last(
    my_moves: MoveHistory, opponent_moves: MoveHistory, context: Any | None
) -> tuple[Move, Any | None]:
    """
    Plays the move that beats the last played move
    """
    if len(opponent_moves) == 0:
        return Move.ROCK, None

    return get_counter(opponent_moves[-1]), None


def strat_beats_modal(
    my_moves: MoveHistory, opponent_moves: MoveHistory, context: Any | None
) -> tuple[Move, Any | None]:
    """
    Picks the move that beats the modal move among the opponents moves
    """
    if len(opponent_moves) == 0:
        return Move.ROCK, None

    arr = sorted(list(Counter(opponent_moves).items()), key=lambda x: x[1])

    return get_counter(arr[-1][0]), None


def strat_paper_only(
    my_moves: MoveHistory, opponent_moves: MoveHistory, context: Any | None
) -> tuple[Move, Any | None]:
    """
    A primitive and bad strategy, that only plays paper
    """

    return Move.PAPER, None


def strat_R2P2S6(
    my_moves: MoveHistory, opponent_moves: MoveHistory, context: Any | None
) -> tuple[Move, Any | None]:
    """
    Plays randomly in a 2:2:6 ratio
    """
    r = random.random()
    if r < 0.2:
        return Move.ROCK, None
    elif r < 0.4:
        return Move.PAPER, None
    else:
        return Move.SCISSORS, None


def strat_random_strat(
    my_moves: MoveHistory, opponent_moves: MoveHistory, context: Any | None
) -> tuple[Move, Any | None]:
    """
    A primitive strategy which fully randomizes its moves, it is
    interesting that this strategy is unexploitable, it will have
    an equal score with all other strategies
    """

    return random.choice(list(Move)), None


def strat_rock_only(
    my_moves: MoveHistory, opponent_moves: MoveHistory, context: Any | None
) -> tuple[Move, Any | None]:
    """
    A primitive and bad strategy, that only plays rock
    """

    return Move.ROCK, None


def strat_rock_or_paper(
    my_move: MoveHistory, opponent_move: MoveHistory, context: Any | None
) -> tuple[Move, Any | None]:
    """
    A primitive strategy which plays rock or scissors randomly,
    a twist on random_strat, but should be way worse
    """

    return random.choice([Move.ROCK, Move.PAPER]), None


def strat_RPS_cyclic(
    my_moves: MoveHistory, opponent_moves: MoveHistory, context: Any | None
) -> tuple[Move, Any | None]:
    """
    Plays Rock->Paper->Scissors in a cycle
    """

    return Move(len(my_moves) % 3), None


def strat_scissors_only(
    my_moves: MoveHistory, opponent_moves: MoveHistory, context: Any | None
) -> tuple[Move, Any | None]:
    """
    A primitive and bad strategy, that only plays scissors
    """

    return Move.SCISSORS, None
