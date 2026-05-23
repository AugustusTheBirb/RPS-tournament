"""
Module that provides helper functions and classes for
the strategies that compete in the RPS tournament.
"""

from enum import IntEnum
from typing import TYPE_CHECKING, Any

import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    from collections.abc import Sequence


class Move(IntEnum):
    """An enum, that represents a RPS move."""

    ROCK = 0
    PAPER = 1
    SCISSORS = 2


MOVE_LETTERS = {
    Move.ROCK: "R",
    Move.PAPER: "P",
    Move.SCISSORS: "S",
}
LETTER_TO_MOVE = {v: k for k, v in MOVE_LETTERS.items()}


MOVE_PAIR_LETTERS = {
    (Move.ROCK, Move.ROCK): "R",
    (Move.ROCK, Move.PAPER): "A",
    (Move.ROCK, Move.SCISSORS): "B",
    (Move.PAPER, Move.ROCK): "C",
    (Move.PAPER, Move.PAPER): "P",
    (Move.PAPER, Move.SCISSORS): "D",
    (Move.SCISSORS, Move.ROCK): "E",
    (Move.SCISSORS, Move.PAPER): "F",
    (Move.SCISSORS, Move.SCISSORS): "S",
}
LETTER_TO_MOVE_PAIR = {v: k for k, v in MOVE_PAIR_LETTERS.items()}

MoveHistory = NDArray[np.object_]


def is_suffix(base: Sequence[Any], suffix: Sequence[Any]) -> bool:
    """
    Check if one sequence is a suffix of the other.

    Args:
        base: A sequence of T type variables.
        suffix: A sequence of T type variables, possible suffix of base.

    Returns:
        A bool if the suffix is suffix or not.

    """
    if not suffix:
        return True

    return base[-len(suffix) :] == suffix


def move_pair_list_to_str(move_list: list[tuple[Move, Move]]) -> str:
    """
    Convert a list of move pairs into a string, can be useful
    for hashing.

    Args:
        move_list: A list of RPS moves
    Returns:
        String made up with 'R', 'A', 'B', 'C', 'P', 'D', 'E', 'F', 'S'

    """
    return "".join(MOVE_PAIR_LETTERS[move] for move in move_list)


def move_list_to_str(move_list: list[Move]) -> str:
    """
    Convert a move list into a string, can be useful
    for hashing.

    Args:
        move_list: A list of RPS moves.

    Returns:
        String made up with 'R', 'P', 'S'.

    """
    return "".join(MOVE_LETTERS[move] for move in move_list)


def resolve_moves(move_1: Move, move_2: Move) -> tuple[int, int]:
    """
    Get moves of two players and resolves how player scores will change.

    Args:
        move_1: Move of the first player (rock, paper or scissors).
        move_2: Move of the second player (rock, paper or scissors).

    Returns:
        delta_1: An integer of how will the score of the first player change.
        delta_2: An integer of how will the score of the second player change.

    """
    result_matrix = [
        [(0, 0), (-1, 1), (1, -1)],
        [(1, -1), (0, 0), (-1, 1)],
        [(-1, 1), (1, -1), (0, 0)],
    ]

    #    R    P    S
    # R 0,0  -1,1  1,-1
    # P 1,-1  0,0  -1,1
    # S -1,1  1,-1  0,0

    return result_matrix[move_1][move_2]


def resolve_move_lists(moves_1: list[Move], moves_2: list[Move]) -> tuple[int, int]:
    """
    Get move lists of two players and resolves how player scores will change.

    Args:
        moves_1: Moves of the first player (rock, paper or scissors).
        moves_2: Moves of the second player (rock, paper or scissors).

    Returns:
        delta_1: An integer of how will the score of the first player change.
        delta_2: An integer of how will the score of the second player change.

    """
    sum_1: int = 0
    sum_2: int = 0

    for i in range(len(moves_1)):
        result: tuple[int, int] = resolve_moves(moves_1[i], moves_2[i])
        sum_1 += result[0]
        sum_2 += result[1]

    return (sum_1, sum_2)


def str_to_move_list(string: str) -> list[Move]:
    """
    Convert a string into a move list.

    Args:
        string: String made up with 'R', 'P', 'S'.

    Returns:
        A list of RPS moves.

    """
    return [LETTER_TO_MOVE[c] for c in string]


def str_to_move_pair_list(string: str) -> list[tuple[Move, Move]]:
    """
    Convert a string into a list of move pairs.

    Args:
        string: String made up with
            'R', 'A', 'B', 'C', 'P', 'D', 'E', 'F', 'S'.

    Returns:
        A list of RPS move pairs.

    """
    return [LETTER_TO_MOVE_PAIR[c] for c in string]
