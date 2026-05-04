import random

from utils import Move, MoveHistory

# pyright: reportUnusedParameter=false


def random_strat(my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
    """
    A primitive strategy which fully randomizes its moves, it is
    interesting that this strategy is unexploitable, it will have
    an equal score with all other strategies

    Args:
        my_moves: A history of this strategy moves this game
        opponent_moves: A history of opponent strategy moves this game
    Returns:
        A move this strategy will make next
    """
    return random.choice(list(Move))


def rock_or_paper(my_move: MoveHistory, opponent_move: MoveHistory) -> Move:
    """
    A primitive strategy which plays rock or scissors randomly,
    a twist on random_strat, but should be way worse

    Args:
        my_moves: A history of this strategy moves this game
        opponent_moves: A history of opponent strategy moves this game
    Returns:
        A move this strategy will make next
    """
    return random.choice([Move.ROCK, Move.PAPER])


def rock_only(my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
    """
    A primitive and bad strategy, that only plays rock

    Args:
        my_moves: A history of this strategy moves this game
        opponent_moves: A history of opponent strategy moves this game
    Returns:
        A move this strategy will make next
    """
    return Move.ROCK


def paper_only(my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
    """
    A primitive and bad strategy, that only plays paper

    Args:
        my_moves: A history of this strategy moves this game
        opponent_moves: A history of opponent strategy moves this game
    Returns:
        A move this strategy will make next
    """
    return Move.PAPER


def scissors_only(my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
    """
    A primitive and bad strategy, that only plays scissors

    Args:
        my_moves: A history of this strategy moves this game
        opponent_moves: A history of opponent strategy moves this game
    Returns:
        A move this strategy will make next
    """
    return Move.SCISSORS


def example_strategy(my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
    """
    Author: Joe

    A strategy, that plays the opponent strategy last move, always starts
    with rock

    Args:
        my_moves: A history of this strategy moves this game
        opponent_moves: A history of opponent strategy moves this game
    Returns:
        A move this strategy will make next
    """
    if 0 < len(opponent_moves):
        return opponent_moves[-1]
    else:
        return Move.ROCK
