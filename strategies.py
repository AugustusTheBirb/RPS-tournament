import random
from collections import Counter

from utils import Move, MoveHistory

# pyright: reportUnusedParameter=false

"""
Args:
    my_moves: A history of this strategy moves this game
    opponent_moves: A history of opponent strategy moves this game
Returns:
    A move this strategy will make next
"""


def random_strat(my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
    """
    A primitive strategy which fully randomizes its moves, it is
    interesting that this strategy is unexploitable, it will have
    an equal score with all other strategies
    """

    return random.choice(list(Move))


def rock_or_paper(my_move: MoveHistory, opponent_move: MoveHistory) -> Move:
    """
    A primitive strategy which plays rock or scissors randomly,
    a twist on random_strat, but should be way worse
    """

    return random.choice([Move.ROCK, Move.PAPER])


def rock_only(my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
    """
    A primitive and bad strategy, that only plays rock
    """

    return Move.ROCK


def paper_only(my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
    """
    A primitive and bad strategy, that only plays paper
    """

    return Move.PAPER


def scissors_only(my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
    """
    A primitive and bad strategy, that only plays scissors
    """

    return Move.SCISSORS


def RPS_cyclic(my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
    """
    Plays Rock->Paper->Scissors in a cycle
    """

    return len(my_moves) % 3


def R2P2S6(my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
    """
    Plays randomly in a 2:2:6 ratio
    """
    r = random.random()
    if r < 0.2:
        return Move.ROCK
    elif r < 0.4:
        return Move.PAPER
    else:
        return Move.SCISSORS


def beats_last(my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
    """
    Plays the move that beats the last played move
    """
    if len(opponent_moves) == 0:
        return Move.ROCK

    move_dict = {
        Move.PAPER: Move.SCISSORS,
        Move.SCISSORS: Move.ROCK,
        Move.ROCK: Move.PAPER,
    }

    return move_dict[opponent_moves[-1]]


def beats_modal(my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
    """
    Picks the move that beats the modal move among the opponents moves
    """
    if len(opponent_moves) == 0:
        return Move.ROCK

    arr = sorted(list(Counter(opponent_moves).items()), key=lambda x: x[1])

    move_dict = {
        Move.PAPER: Move.SCISSORS,
        Move.SCISSORS: Move.ROCK,
        Move.ROCK: Move.PAPER,
    }

    return move_dict[arr[-1][0]]
