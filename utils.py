from enum import IntEnum
from typing import Callable, Sequence

import numpy as np
from numpy.typing import NDArray


class Move(IntEnum):
    ROCK = 0
    PAPER = 1
    SCISSORS = 2


MOVE_LETTERS = {
    Move.ROCK: "R",
    Move.PAPER: "P",
    Move.SCISSORS: "S",
}
LETTER_TO_MOVE = {v: k for k, v in MOVE_LETTERS.items()}


MoveHistory = NDArray[np.object_]
Strategy = Callable[[MoveHistory, MoveHistory], Move]


def get_counter(move_to_counter: Move) -> Move:
    """
    Give a move that counter your move

    Args:
        move_to_counter: An RPS move you want to beat
    Returns:
        A move that beats the provided move
    """
    if move_to_counter == Move.ROCK:
        return Move.PAPER
    elif move_to_counter == Move.PAPER:
        return Move.SCISSORS
    elif move_to_counter == Move.SCISSORS:
        return Move.ROCK


def is_suffix[T](base: Sequence[T], suffix: Sequence[T]) -> bool:
    """
    Checks if one sequence is a suffix of the other

    Args:
        base: A sequence of T type variables
        suffix: A sequence of T type variables, possible suffix of base
    Returns:
        A bool if the suffix is suffix or not
    """
    if not suffix:
        return True

    return base[-len(suffix):] == suffix


def move_list_to_str(move_list: list[Move]) -> str:
    """
    Converts a move list into a string, can be useful
    for hashing

    Args:
        move_list: A list of RPS moves
    Returns:
        String made up with 'R', 'P', 'S'
    """
    return "".join(MOVE_LETTERS[move] for move in move_list)


def resolve_moves(move_1: Move, move_2: Move) -> tuple[int, int]:
    """
    Gets moves of two players and resolves how player scores will change

    Args:
        move_1: Move of the first player (rock, paper or scissors)
        move_2: Move of the second player (rock, paper or scissors)
    Returns:
        delta_1: An integer of how will the score of the first player change
        delta_2: An integer of how will the score of the second player change
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


def str_to_move_list(string: str) -> list[Move]:
    """
    Converts a string into a move list

    Args:
        string: String made up with 'R', 'P', 'S'
    Returns:
        A list of RPS moves
    """
    return [LETTER_TO_MOVE[c] for c in string]
