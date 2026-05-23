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
    get_rated_substrings_v1,
    is_suffix,
    move_list_to_str,
    move_pair_list_to_str,
    resolve_move_lists,
)

# pyright: reportUnusedParameter=false


class Strategy(ABC):
    def __init__(self) -> None:
        super().__init__()

        self.name: str = "base_strategy_class"

    @abstractmethod
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        """
        (Docstring for all strategies)
        Args:
            my_moves: A history of this strategy moves this game
            opponent_moves: A history of opponent strategy moves this game
        Returns:
            move: A move this strategy will make next
        """

        pass

    @staticmethod
    def get_counter_move(move: Move, level: int = 1) -> Move:
        """
        Gives a move that counters the given moveste

        Args:
            move_to_counter: An RPS move you want to beat
            level=1: How many times to counter a move
        Returns:
            A move that beats the provided move
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
        Gives a first move, if not sure

        Returns:
            Returns a first standardised move
        """

        return Strategy.get_random_move()

    @staticmethod
    def get_random_move() -> Move:
        """
        Returns a random move

        Returns:
            A random Move
        """

        return random.choice(list(Move))


class StratBeatsLast(Strategy):
    """
    Plays the move that beats the last played move
    """

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "beats_last"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        if len(opponent_moves) == 0:
            return self.get_first_move()

        return self.get_counter_move(opponent_moves[-1])


class StratBeatsLastMeta1(Strategy):
    """
    Plays the move that beats the move that beats the last played move
    """

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "beats_last_meta"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        meta_flag: bool = False

        if len(opponent_moves) == 0:
            return self.get_first_move()

        if len(opponent_moves) >= 50:
            my_score_50: int = resolve_move_lists(
                list(my_moves[-50:-1]), list(opponent_moves[-50:-1])
            )[0]
            if my_score_50 < 5:
                meta_flag = True

        if meta_flag:
            return self.get_counter_move(my_moves[-1], level=2)
        else:
            return self.get_counter_move(opponent_moves[-1])


class StratBeatsModal(Strategy):
    """
    Picks the move that beats the modal move among the opponents moves
    """

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "beats_modal"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        if len(opponent_moves) == 0:
            return self.get_first_move()

        most_common_move: Move
        most_common_move, _ = sorted(
            list(Counter(opponent_moves).items()), key=lambda x: x[1]
        )[-1]

        return self.get_counter_move(most_common_move)


class StratPaperOnly(Strategy):
    """
    A primitive and bad strategy, that only plays paper
    """

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "paper"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        return Move.PAPER


class StratPatternBeater(Strategy):
    """
    Plays the move that would counter what a pattern matcher would predict it
    would play. Result is that it confuses 1d pattern matchers into playing the
    the same move over and over again. Exploits this.

    Author: AugustusTheBirb
    """

    def __init__(self, pattern_length: int = 3) -> None:
        super().__init__()

        self.name: str = "pattern_beater"

        self.pattern_length: int = pattern_length

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

        if 10 < len(my_moves):
            if np.all(opponent_moves[-self.pattern_length :] == opponent_moves[-1]):
                return self.get_counter_move(opponent_moves[-1])

            key = tuple(self.my_list[-self.pattern_length :])
            move_appearance_count = self.patterns.get(key, new_key_value)

            predicted_move: Move
            predicted_move, _ = sorted(
                list(move_appearance_count.items()), key=lambda x: x[1]
            )[-1]

            return self.get_counter_move(
                predicted_move, level=2
            )

        return self.get_random_move()


class StratPatternmatcher1dV1(Strategy):
    """
    A more complex strategy, which tries to find a pattern in the
    opponets moves, to defeat the opponent, it is quite dependant
    on its parameters

    Author: lukassta
    """

    def __init__(
        self,
        max_sublist_length: int = 4,
        base_sublist_score: int = 1,
        letter_score_mult: int = 3,
    ) -> None:
        super().__init__()

        self.name: str = "patternmatcher_1d"

        self.max_sublist_length: int = max_sublist_length
        self.base_sublist_score: int = base_sublist_score
        self.letter_score_mult: int = letter_score_mult

        self.iteration: int = 0
        self.rated_substrings: dict[str, float] = {}
        self.sorted_substrings: list[tuple[float, str]] = []
        self.opponent_move_string: str = ""

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        self.opponent_move_string += move_list_to_str(
            list(opponent_moves[self.iteration :])
        )

        self.iteration, self.rated_substrings, self.sorted_substrings = (
            get_rated_substrings_v1(
                self.opponent_move_string,
                min_lenght=1,
                max_lenght=self.max_sublist_length,
                base_score=self.base_sublist_score,
                letter_score_mult=self.letter_score_mult,
                context=(self.iteration, self.rated_substrings, self.sorted_substrings),
            )
        )

        for _, substring in self.sorted_substrings:
            if is_suffix(self.opponent_move_string, substring[:-1]):
                predicted_move: Move = LETTER_TO_MOVE[substring[-1]]

                return self.get_counter_move(predicted_move)

        return self.get_random_move()


class StratPatternmatcher2dV1(Strategy):
    """
    A more complex strategy, which tries to find a pattern in its and
    opponent strategy move combinations, to defeat the opponent, it is
    quite dependant on its parameters

    Author: lukassta
    """

    def __init__(
        self,
        max_sublist_length: int = 4,
        base_sublist_score: int = 2,
        letter_score_mult: int = 9,
    ) -> None:
        super().__init__()

        self.name: str = "patternmatcher_2d"

        self.max_sublist_length: int = max_sublist_length
        self.base_sublist_score: int = base_sublist_score
        self.letter_score_mult: int = letter_score_mult

        self.iteration: int = 0
        self.rated_substrings: dict[str, float] = {}
        self.sorted_substrings: list[tuple[float, str]] = []
        self.move_pair_string: str = ""

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        self.move_pair_list: list[tuple[Move, Move]] = list(
            zip(my_moves[self.iteration :], opponent_moves[self.iteration :])
        )
        self.move_pair_string += move_pair_list_to_str(self.move_pair_list)

        self.iteration, self.rated_substrings, self.sorted_substrings = (
            get_rated_substrings_v1(
                self.move_pair_string,
                min_lenght=1,
                max_lenght=self.max_sublist_length,
                base_score=self.base_sublist_score,
                letter_score_mult=self.letter_score_mult,
                context=(self.iteration, self.rated_substrings, self.sorted_substrings),
            )
        )

        for _, substring in self.sorted_substrings:
            if is_suffix(self.move_pair_string, substring[:-1]):
                predicted_move: Move = LETTER_TO_MOVE_PAIR[substring[-1]][1]

                return self.get_counter_move(predicted_move)

        return self.get_random_move()


class StratR2P2S6(Strategy):
    """
    Plays randomly in a 2:2:6 ratio
    """

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "r2p2s6"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        r = random.random()
        if r < 0.2:
            return Move.ROCK
        elif r < 0.4:
            return Move.PAPER
        else:
            return Move.SCISSORS


class StratRandom(Strategy):
    """
    A primitive strategy which fully randomizes its moves, it is
    interesting that this strategy is unexploitable, it will have
    an equal score with all other strategies
    """

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "random"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        return self.get_random_move()


class StratRockOnly(Strategy):
    """
    A primitive and bad strategy, that only plays rock
    """

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "rock"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        return Move.ROCK


class StratRockOrPaper(Strategy):
    """
    A primitive strategy which plays rock or scissors randomly,
    a twist on random_strat, but should be way worse
    """

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "rock_paper"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        return random.choice([Move.ROCK, Move.PAPER])


class StratRPSCyclic(Strategy):
    """
    Plays Rock->Paper->Scissors in a cycle
    """

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "cyclic"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        return Move(len(my_moves) % 3)


class StratScissorsOnly(Strategy):
    """
    A primitive and bad strategy, that only plays scissors
    """

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "scissors"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        return Move.SCISSORS


class StratBeatsOpDistribution(Strategy):
    """
    Plays a move that beats a move randomly chosen from the distribution
    of opponents moves
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
            list(Move), weights=list(self.appearance_count.values()), k=1
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
