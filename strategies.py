"""
Module that implements strategies that compete in the RPS tournament.

To add a strategy simply implement the abstact class Strategy in this file,
and it will automatically be registered

To add a strategy group, create a variable of type list[Strategy] and name
it so is starts with "group_".
"""

import bisect
import random
from abc import ABC, abstractmethod
from collections import Counter
from typing import override

import numpy as np

from utils import (
    LETTER_TO_MOVE,
    LETTER_TO_MOVE_PAIR,
    Move,
    MoveHistory,
    is_suffix,
    move_list_to_str,
    move_pair_list_to_str,
    resolve_move_lists,
)

# pyright: reportUnusedParameter=false


class Strategy(ABC):
    """An interface for all RPS strategies."""

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "base_strategy_class"

    @abstractmethod
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        """
        Make a move accorind to previous move history.

        Args:
            my_moves: A history of this strategy moves this game.
            opponent_moves: A history of opponent strategy moves this game.

        Returns:
            A move this strategy will make next.

        """

    @staticmethod
    def get_counter_move(move: Move, level: int = 1) -> Move:
        """
        Give a move that counters the given moveste.

        Args:
            move: An RPS move you want to beat.
            level: How many times to counter a move.

        Returns:
            A move that beats the provided move.

        """
        for _ in range(level):
            if move == Move.ROCK:
                move = Move.PAPER
            elif move == Move.PAPER:
                move = Move.SCISSORS
            elif move == Move.SCISSORS:
                move = Move.ROCK

        return move

    @staticmethod
    def get_first_move() -> Move:
        """
        Give a first move, if not sure.

        Returns:
            Returns a first standardised move.

        """
        return Strategy.get_random_move()

    @staticmethod
    def get_random_move() -> Move:
        """
        Return a random move.

        Returns:
            A random Move.

        """
        return random.choice(list(Move))


class StratBeatsLast(Strategy):
    """Play the move that beats the last played move."""

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "beats_last"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        if len(opponent_moves) == 0:
            return self.get_first_move()

        return self.get_counter_move(opponent_moves[-1])


class StratBeatsLastMeta1(Strategy):
    """Play the move that beats the move that beats the last played move."""

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "beats_last_meta"

        self.evaluated_move_count: int = 50
        self.meta_move_threshhold: int = 5

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:

        if len(opponent_moves) <= self.evaluated_move_count:
            return self.get_first_move()

        my_evaluated_move_score: int = resolve_move_lists(
            list(my_moves[-self.evaluated_move_count : -1]),
            list(opponent_moves[-self.evaluated_move_count : -1]),
        )[0]

        if my_evaluated_move_score < self.meta_move_threshhold:
            return self.get_counter_move(my_moves[-1], level=2)

        return self.get_counter_move(opponent_moves[-1])


class StratBeatsModal(Strategy):
    """Pick the move that beats the modal move among the opponents moves."""

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "beats_modal"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        if len(opponent_moves) == 0:
            return self.get_first_move()

        most_common_move: Move
        most_common_move, _ = sorted(
            Counter(opponent_moves).items(),
            key=lambda x: x[1],
        )[-1]

        return self.get_counter_move(most_common_move)


class StratPaperOnly(Strategy):
    """A primitive and bad strategy, that only plays paper."""

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "paper"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        return Move.PAPER


class StratPatternBeater(Strategy):
    """
    Play the move that would counter what a pattern matcher would predict it
    would play. Result is that it confuses 1d pattern matchers into playing the
    the same move over and over again. Exploits this.

    Author: AugustusTheBirb
    """

    def __init__(self, pattern_length: int = 3) -> None:
        super().__init__()

        self.name: str = "pattern_beater"

        self.pattern_length: int = pattern_length
        self.first_random_move_count: int = 10

        self.my_list: list[Move] = []
        self.patterns: dict[tuple[Move, ...], dict[Move, int]] = {}

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        new_key_value = {Move.ROCK: 0, Move.PAPER: 0, Move.SCISSORS: 0}

        if len(self.my_list) < len(my_moves):
            new_move: Move = my_moves[-1]

            if len(self.my_list) >= self.pattern_length:
                key = tuple(self.my_list[-self.pattern_length :])

                if key not in self.patterns:
                    self.patterns[key] = new_key_value

                self.patterns[key][new_move] += 1

            self.my_list.append(new_move)

        if self.first_random_move_count < len(my_moves):
            if np.all(opponent_moves[-self.pattern_length :] == opponent_moves[-1]):
                return self.get_counter_move(opponent_moves[-1])

            key = tuple(self.my_list[-self.pattern_length :])
            move_appearance_count = self.patterns.get(key, new_key_value)

            predicted_move: Move
            predicted_move, _ = sorted(
                move_appearance_count.items(),
                key=lambda x: x[1],
            )[-1]

            return self.get_counter_move(predicted_move, level=2)

        return self.get_random_move()


class PatternmatcherStrategyV1(Strategy, ABC):
    """
    An interface for patternmatcher v1 strategies.

    Author: lukassta
    """

    def __init__(
        self,
        min_sublist_length: int = 1,
        max_sublist_length: int = 4,
        base_sublist_score: int = 1,
        letter_score_mult: int = 3,
    ) -> None:
        super().__init__()

        self.name: str = "patternmatcher_1d"

        self.min_sublist_length: int = min_sublist_length
        self.max_sublist_length: int = max_sublist_length
        self.base_sublist_score: int = base_sublist_score
        self.letter_score_mult: int = letter_score_mult

        self.processed_move_count: int = 0
        self.rated_substrings: dict[str, float] = {}
        self.sorted_substrings: list[tuple[float, str]] = []
        self.move_string: str = ""

    def update_rated_substrings(
        self,
        superstring: str,
    ) -> None:
        """
        Return all substrings in a string rated by occurance
        chance.

        Score calculations logic:
        score (per occurance)= base + letter_count ^ mult.

        it tries to ballance shorter letter combinations with
        longer ones

        R will be 3 times more common that RR
        RR will be 3 times more common that RRR

        thus a sane letter_score_mult=4, because it slightly
        favours longer substrings

        Args:
            superstring: a string to find all substrings.

        """
        for i in range(self.processed_move_count, len(superstring) + 1):
            for letter_count in range(
                self.min_sublist_length,
                self.max_sublist_length + 1,
            ):
                if i - letter_count < 0:
                    continue

                substring = superstring[i - letter_count : i]
                score = self.base_sublist_score + self.letter_score_mult**letter_count

                if substring in self.rated_substrings:
                    self.sorted_substrings.remove(
                        (self.rated_substrings[substring], substring),
                    )
                    self.rated_substrings[substring] -= score
                else:
                    self.rated_substrings[substring] = -score

                bisect.insort(
                    self.sorted_substrings,
                    (self.rated_substrings[substring], substring),
                )

        self.processed_move_count = len(superstring)


class StratPatternmatcher1dV1(PatternmatcherStrategyV1):
    """
    A more complex strategy, which tries to find a pattern in the
    opponets moves, to defeat the opponent, it is quite dependant
    on its parameters.

    Author: lukassta
    """

    def __init__(
        self,
        min_sublist_length: int = 1,
        max_sublist_length: int = 4,
        base_sublist_score: int = 1,
        letter_score_mult: int = 3,
    ) -> None:
        super().__init__(
            min_sublist_length=min_sublist_length,
            max_sublist_length=max_sublist_length,
            base_sublist_score=base_sublist_score,
            letter_score_mult=letter_score_mult,
        )

        self.name: str = "patternmatcher_1d"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        self.move_string: str
        self.move_string += move_list_to_str(
            list(opponent_moves[self.processed_move_count :]),
        )

        self.update_rated_substrings(
            self.move_string,
        )

        for _, substring in self.sorted_substrings:
            if is_suffix(self.move_string, substring[:-1]):
                predicted_move: Move = LETTER_TO_MOVE[substring[-1]]

                return self.get_counter_move(predicted_move)

        return self.get_random_move()


class StratPatternmatcher2dV1(PatternmatcherStrategyV1):
    """
    A more complex strategy, which tries to find a pattern in its and
    opponent strategy move combinations, to defeat the opponent, it is
    quite dependant on its parameters.

    Author: lukassta
    """

    def __init__(
        self,
        min_sublist_length: int = 1,
        max_sublist_length: int = 4,
        base_sublist_score: int = 2,
        letter_score_mult: int = 9,
    ) -> None:
        super().__init__(
            min_sublist_length=min_sublist_length,
            max_sublist_length=max_sublist_length,
            base_sublist_score=base_sublist_score,
            letter_score_mult=letter_score_mult,
        )

        self.name: str = "patternmatcher_2d"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        self.move_pair_list: list[tuple[Move, Move]] = list(
            zip(
                my_moves[self.processed_move_count :],
                opponent_moves[self.processed_move_count :],
                strict=True,
            ),
        )
        self.move_string: str
        self.move_string += move_pair_list_to_str(self.move_pair_list)

        self.update_rated_substrings(
            self.move_string,
        )

        for _, substring in self.sorted_substrings:
            if is_suffix(self.move_string, substring[:-1]):
                predicted_move: Move = LETTER_TO_MOVE_PAIR[substring[-1]][1]

                return self.get_counter_move(predicted_move)

        return self.get_random_move()


class StratR2P2S6(Strategy):
    """Play randomly in a 2:2:6 ratio."""

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "r2p2s6"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        rock_chance: float = 0.2
        paper_chance: float = 0.2

        r = random.random()
        if r < rock_chance:
            return Move.ROCK
        if r < rock_chance + paper_chance:
            return Move.PAPER
        return Move.SCISSORS


class StratRandom(Strategy):
    """
    A primitive strategy which fully randomizes its moves, it is
    interesting that this strategy is unexploitable, it will have
    an equal score with all other strategies.
    """

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "random"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        return self.get_random_move()


class StratRockOnly(Strategy):
    """A primitive and bad strategy, that only plays rock."""

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "rock"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        return Move.ROCK


class StratRockOrPaper(Strategy):
    """
    A primitive strategy which plays rock or scissors randomly,
    a twist on random_strat, but should be way worse.
    """

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "rock_paper"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        return random.choice([Move.ROCK, Move.PAPER])


class StratRPSCyclic(Strategy):
    """Play Rock->Paper->Scissors in a cycle."""

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "cyclic"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        return Move(len(my_moves) % 3)


class StratScissorsOnly(Strategy):
    """A primitive and bad strategy, that only plays scissors."""

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "scissors"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        return Move.SCISSORS


class StratBeatsOpDistribution(Strategy):
    """
    Play a move that beats a move randomly chosen from the distribution
    of opponents moves.
    """

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "beats_distribution"

        self.appearance_count: dict[Move, int] = {
            Move.ROCK: 0,
            Move.PAPER: 0,
            Move.SCISSORS: 0,
        }

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        if len(opponent_moves) == 0:
            return self.get_first_move()

        self.appearance_count[opponent_moves[-1]] += 1

        predicted_move: Move = random.choices(
            list(Move),
            weights=list(self.appearance_count.values()),
            k=1,
        )[0]

        return self.get_counter_move(predicted_move)


group_bad: list[Strategy] = [
    StratRockOnly(),
    StratScissorsOnly(),
    StratPaperOnly(),
]
group_random: list[Strategy] = [
    StratRandom(),
    StratR2P2S6(),
    StratRockOrPaper(),
]
group_primitive: list[Strategy] = [
    StratRPSCyclic(),
    StratBeatsLast(),
    StratBeatsModal(),
    StratBeatsOpDistribution(),
]
group_meta: list[Strategy] = [StratBeatsLastMeta1()]
group_pattern: list[Strategy] = [
    StratPatternmatcher1dV1(),
    StratPatternmatcher2dV1(),
]
