# RPS tournament
A repo for running rock-paper-scissors tournaments with lots of strategies

## To contribute
Read this article [Rock Paper Scissors is not solved, in practice](https://open.substack.com/pub/inchpin/p/rock-paper-scissors-is-not-solved).

Develop a strategy of your own.

Run, to format and check your code:
```bash
black strategies.py
isort strategies.py
flake8 strategies.py
```

Submit it via this [form](https://forms.gle/uk3tAW2y4vxVbxyLA)

**Because performance in this tournament depends on the population of other strategies present, there is only one submission allowed per participant.**

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

The '**random**' library is imported and functions from it can be used, there are also two helper functions utils.convert_to_name() which converts a move id to a move name, and utils.convert_to_id which converts a name to an id


An example strategy:
```python
def strat_beats_last(
    my_moves: MoveHistory, opponent_moves: MoveHistory, context: Any | None
) -> tuple[Move, Any | None]:
    """
    Plays the move that beats the last played move

    Author: Alice, Bob, John
    """
    if len(opponent_moves) == 0:
        return Move.ROCK, None


    return get_counter(opponent_moves[-1]), None
```

To verify your strategies performace you can clone the repo, add your strategies function to the strategies.py file and run the run_tournament.py file.
