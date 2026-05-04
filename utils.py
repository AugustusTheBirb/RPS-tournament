from enum import IntEnum
from typing import Callable

import numpy as np
from numpy.typing import NDArray


class Move(IntEnum):
    ROCK = 0
    PAPER = 1
    SCISSORS = 2


MoveHistory = NDArray[np.object_]
Strategy = Callable[[MoveHistory, MoveHistory], Move]


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
