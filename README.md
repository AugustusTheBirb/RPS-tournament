# RPS tournament
A repo for running rock-paper-scissors tournaments with lots of strategies

To submit a strategy fill out this [form](https://forms.gle/uk3tAW2y4vxVbxyLA)

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

A strategy is a python function that takes in a move history ('my_moves' and 'opponent_moves'), both n length arrays whose values are from the set ['rock', 'paper', 'scissors'], and returns one of the strings from the same set. It should contain a comment with your name/pseudonym.

The '**random**' library is imported and functions from it can be used, there are also two helper functions utils.convert_to_name() which converts a move id to a move name, and utils.convert_to_id which converts a name to an id


An example strategy:
```python
def example_strategy(my_moves, opponent_moves):
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
```

To verify your strategies performace you can clone the repo, add your strategies function to the strategies.py file and run the run_tournament.py file.
