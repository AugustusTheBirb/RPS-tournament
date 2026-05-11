import random
from collections import Counter
from typing import Any
import numpy as np

from sortedcontainers import SortedList

from utils import (
    LETTER_TO_MOVE,
    LETTER_TO_MOVE_PAIR,
    Move,
    MoveHistory,
    Strategy,
    get_counter,
    get_rated_substrings_v1,
    is_suffix,
    move_list_to_str,
    move_pair_list_to_str,
    resolve_move_lists,
)

# pyright: reportUnusedParameter=false, reportExplicitAny=false

"""
(Docstring for all strategies)
Args:
    my_moves: A history of this strategy moves this game
    opponent_moves: A history of opponent strategy moves this game
    context: Can be any variable, if unused then None, used for
        optimisation
Returns:
    move: A move this strategy will make next
    context: Can be any variable, if unused then None
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


def strat_beats_last_meta1(
    my_moves: MoveHistory, opponent_moves: MoveHistory, context: Any | None
) -> tuple[Move, Any | None]:
    """
    Plays the move that beats the move that beats the last played move
    """
    meta_flag: bool = False

    if len(opponent_moves) == 0:
        return random.choice(list(Move)), None

    if len(opponent_moves) >= 50:
        my_score_50 = resolve_move_lists(my_moves[-50:-1], opponent_moves[-50:-1])[0]
        if my_score_50 < 5:
            meta_flag = True

    move_beats_last: Move = get_counter(opponent_moves[-1])

    if meta_flag:
        return get_counter(get_counter(my_moves[-1])), None
    else:
        return move_beats_last, None


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


def strat_pattern_beater(
    my_moves: MoveHistory, opponent_moves: MoveHistory, context: Any | None
) -> tuple[Move, Any | None]:
    """
    Plays the move that would counter what a pattern matcher would predict it
    would play. Result is that it confuses 1d pattern matchers into playing the
    the same move over and over again. Exploits this.

    Author: AugustusTheBirb
    """

    pattern_length: int = 3

    if context is None:
        context = ([], {})
    my_list, patterns = context

    # update context
    if len(my_moves) > len(my_list):
        new_move = int(my_moves[-1])
        if len(my_list) >= pattern_length:
            key = tuple(my_list[-pattern_length:])
            if key not in patterns:
                patterns[key] = {0: 0, 1: 0, 2: 0}
            patterns[key][new_move] += 1
        my_list.append(new_move)

    if len(my_moves) > 10:

        if np.all(opponent_moves[-pattern_length : ] == opponent_moves[-1]):
            return get_counter(opponent_moves[-1]), context

        key = tuple(my_list[-pattern_length:])
        d = patterns.get(key, {0: 0, 1: 0, 2: 0})

        arr = sorted(list(d.items()), key=lambda x: x[1])

        return get_counter(get_counter(arr[-1][0])), context
    else:
        return random.randint(0,2), context


def strat_patternmatcher_1d_v1(
    my_moves: MoveHistory,
    opponent_moves: MoveHistory,
    context: tuple[int, dict[str, float], SortedList, str] | None,
) -> tuple[Move, tuple[int, dict[str, float], SortedList, str] | None]:
    """
    A more complex strategy, which tries to find a pattern in the
    opponets moves, to defeat the opponent, it is quite dependant
    on its parameters

    Author: lukassta
    """
    # ========PARAMETERS========
    MAX_SUBLIST_LENGTH = 4
    BASE_SUBLIST_SCORE = 1
    LETTER_SCORE_MULT = 3
    # ==========================

    if context is None:
        context = (0, {}, SortedList(), "")

    iteration: int
    rated_substrings: dict[str, float]
    sorted_substrings: SortedList
    opponent_move_string: str
    iteration, rated_substrings, sorted_substrings, opponent_move_string = context

    opponent_move_string += move_list_to_str(list(opponent_moves[iteration:]))

    iteration, rated_substrings, sorted_substrings = get_rated_substrings_v1(
        opponent_move_string,
        min_lenght=1,
        max_lenght=MAX_SUBLIST_LENGTH,
        base_score=BASE_SUBLIST_SCORE,
        letter_score_mult=LETTER_SCORE_MULT,
        context=(iteration, rated_substrings, sorted_substrings),
    )

    for _, substring in reversed(sorted_substrings):
        if is_suffix(opponent_move_string, substring[:-1]):
            predicted_move: Move = LETTER_TO_MOVE[substring[-1]]
            counter_move: Move = get_counter(predicted_move)

            return counter_move, (
                iteration,
                rated_substrings,
                sorted_substrings,
                opponent_move_string,
            )

    return random.choice(list(Move)), (
        iteration,
        rated_substrings,
        sorted_substrings,
        opponent_move_string,
    )


def strat_patternmatcher_2d_v1(
    my_moves: MoveHistory,
    opponent_moves: MoveHistory,
    context: tuple[int, dict[str, float], SortedList, str] | None,
) -> tuple[Move, tuple[int, dict[str, float], SortedList, str] | None]:
    """
    A more complex strategy, which tries to find a pattern in its and
    opponent strategy move combinations, to defeat the opponent, it is
    quite dependant on its parameters

    Author: lukassta
    """
    # ========PARAMETERS========
    MAX_SUBLIST_LENGTH = 4
    BASE_SUBLIST_SCORE = 2
    LETTER_SCORE_MULT = 9
    # ==========================

    if context is None:
        context = (0, {}, SortedList(), "")

    iteration: int
    rated_substrings: dict[str, float]
    sorted_substrings: SortedList
    move_pair_string: str
    iteration, rated_substrings, sorted_substrings, move_pair_string = context

    move_pair_list: list[tuple[Move, Move]] = list(
        zip(my_moves[iteration:], opponent_moves[iteration:])
    )
    move_pair_string += move_pair_list_to_str(move_pair_list)

    iteration, rated_substrings, sorted_substrings = get_rated_substrings_v1(
        move_pair_string,
        min_lenght=1,
        max_lenght=MAX_SUBLIST_LENGTH,
        base_score=BASE_SUBLIST_SCORE,
        letter_score_mult=LETTER_SCORE_MULT,
        context=(iteration, rated_substrings, sorted_substrings),
    )

    for _, substring in reversed(sorted_substrings):
        if is_suffix(move_pair_string, substring[:-1]):
            predicted_move: Move = LETTER_TO_MOVE_PAIR[substring[-1]][1]
            counter_move: Move = get_counter(predicted_move)

            return counter_move, (
                iteration,
                rated_substrings,
                sorted_substrings,
                move_pair_string,
            )

    return random.choice(list(Move)), (
        iteration,
        rated_substrings,
        sorted_substrings,
        move_pair_string,
    )


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


def strat_random(
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


def strat_beats_op_distribution(
    my_moves: MoveHistory, opponent_moves: MoveHistory, context: Any | None
) -> tuple[Move, Any | None]:
    """
    Plays a move that beats a move randomly chosen from the distribution
    of opponents moves
    """
    if not context:
        context = {Move.ROCK: 0, Move.PAPER: 0, Move.SCISSORS: 0}
        return Move(random.randint(0, 2)), context

    context[opponent_moves[-1]] += 1
    n: int = len(opponent_moves)
    weights: list[float] = list(i / n for i in context.values())

    return (
        get_counter(Move(random.choices([0, 1, 2], weights=weights, k=1)[0])),
        context,
    )


group_bad: list[Strategy] = [strat_rock_only, strat_scissors_only, strat_paper_only]
group_random: list[Strategy] = [strat_random, strat_R2P2S6, strat_rock_or_paper]
group_primitive: list[Strategy] = [
    strat_RPS_cyclic,
    strat_beats_last,
    strat_beats_modal,
    strat_beats_op_distribution,
]
group_meta: list[Strategy] = [strat_beats_last_meta1]
group_pattern: list[Strategy] = [strat_patternmatcher_1d_v1, strat_patternmatcher_2d_v1]
