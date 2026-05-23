# RPS tournament
A tournament where bots compete in iterated rock-paper-scissors matches.

## Setup
Have python, uv installed and run
```bash
uv sync
```

## Usage
To run the tournament
```bash
uv run python run_tournament.py -p
```

## What is this tournament
This is a tournament of rock paper scissors strategies, each strategy will play against every other strategy for 1000 moves, repeated 3x to average out some randomness.

Score is determined according to this matrix for each individual move
| | R | P | S |
|---|---|---|---|
| **R** | 0,0 | -1,1 | 1,-1 |
| **P** | 1,-1 | 0,0 | -1,1 |
| **S** | -1,1 | 1,-1 | 0,0 |

Rock beats scissors, scissors beat paper, paper beats rock.

## What is a strategy

A strategy is a python function that takes in a move history ('my_moves' and 'opponent_moves') and a context variable, histories are n length arrays, context can be of any type. Strategy function returns one of the moves (Move.ROCK, Move.PAPER, Move.SCISSORS) from the same set and some context. It should contain a docstring with description of your strategy and your name/pseudonym.

**Pandas, numpy and random libraries are imported and can be freely used, no other external libraries besides these are allowed** There are also some helper functions in the utils.py file.


An example strategy:
```python
class StratBeatsLast(Strategy):
    """
    Play the move that beats the last played move.

    Author: Alice, Bob
    """

    def __init__(self) -> None:
        super().__init__()

        self.name: str = "beats_last"

    @override
    def make_a_move(self, my_moves: MoveHistory, opponent_moves: MoveHistory) -> Move:
        if len(opponent_moves) == 0:
            return self.get_first_move()

        return self.get_counter_move(opponent_moves[-1])
```


## To contribute

This article gives some background information on RPS strategies: [Rock Paper Scissors is not solved, in practice](https://open.substack.com/pub/inchpin/p/rock-paper-scissors-is-not-solved).

Develop a strategy of your own. You can you use the workshop notebook for testing and hyperparameter tuning. To run a strategy in the tournament simply add the function to the *strategies.py* file

You can also try playing against the strategies yourself via the interactive.py file.


Before submittintg run this, to format and check your code:
```bash
uv sync --group dev
uv run ruff format
uv run ruff check
uv run basedpyright
```

Submit it via this [form](https://forms.gle/uk3tAW2y4vxVbxyLA)

**Because performance in this tournament depends on the population of other strategies present, there is only one submission allowed per participant.**
