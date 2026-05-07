from enum import IntEnum
from typing import Any, Callable, Sequence

import numpy as np
from numpy.typing import NDArray
from typing import TypeVar

_T = TypeVar("_T")

# pyright: reportExplicitAny=false


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
Strategy = Callable[[MoveHistory, MoveHistory, Any | None], tuple[Move, Any | None]]


def get_counter(move_to_counter: Move) -> Move:
    """
    Gives a move that counters the given move

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


def get_rated_substringss_v1(
    string: str,
    *,
    min_lenght: int,
    max_lenght: int,
    base_score: int,
    letter_score_mult: int,
    context: tuple[int, dict[str, float]],
) -> tuple[int, dict[str, float]]:
    """
    Returns all substrings in a string rated by occurance
    chance

    Score calculations logic:
    score (per occurance)= base + letter_count ^ mult

    it tries to ballance shorter letter combinations with
    longer ones

    R will be 3 times more common that RR
    RR will be 3 times more common that RRR

    thus a sane letter_score_mult=4, because it slightly
    favours longer substrings

    Args:
        string: a string to find all substrings
        min_lenght: minimum length of substrings
        max_lenght: maximum length of substrings
        base_score: score given to a substring
        letter_score_mult: multiplier of the base score
            for each letter
        context: An int of previoulsy evaluated letters count
            and a dict of perviously found substrings, purely
            an optimisation
    Returns:
        An int of previoulsy evaluated letter count and a
        dict of found substrings as keys, and scores
        as values
    """
    evaluated_moves: int = context[0]
    scored_substrings: dict[str, float] = context[1]

    for i in range(evaluated_moves, len(string)):
        for letter_count in range(min_lenght, max_lenght + 1):
            if i - letter_count <= 0:
                continue

            substring = string[i - letter_count : i]
            score = base_score + letter_score_mult ^ letter_count

            if scored_substrings.__contains__(substring):
                scored_substrings[substring] += score

                continue

            scored_substrings[substring] = score

    sorted_substrings: dict[str, float] = {
        substring: score
        for substring, score in sorted(
            scored_substrings.items(), key=lambda item: item[1], reverse=True
        )
    }

    return len(string), sorted_substrings


def is_suffix(base: Sequence[_T], suffix: Sequence[_T]) -> bool:
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

    return base[-len(suffix) :] == suffix


def move_pair_list_to_str(move_list: list[tuple[Move, Move]]) -> str:
    """
    Converts a list of move pairs into a string, can be useful
    for hashing

    Args:
        move_list: A list of RPS moves
    Returns:
        String made up with 'R', 'A', 'B', 'C', 'P', 'D', 'E', 'F', 'S'
    """
    return "".join(MOVE_PAIR_LETTERS[move] for move in move_list)


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


def str_to_move_list(string: str) -> list[tuple[Move, Move]]:
    """
    Converts a string into a move list

    Args:
        string: String made up with 'R', 'P', 'S'
    Returns:
        A list of RPS moves
    """
    return [LETTER_TO_MOVE[c] for c in string]


def str_to_move_pair_list(string: str) -> list[tuple[Move, Move]]:
    """
    Converts a string into a list of move pairs

    Args:
        string: String made up with
            'R', 'A', 'B', 'C', 'P', 'D', 'E', 'F', 'S'
    Returns:
        A list of RPS move pairs
    """
    return [LETTER_TO_MOVE_PAIR[c] for c in string]