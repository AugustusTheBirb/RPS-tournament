import random
import utils

def random_strat(my_moves, opponent_moves):
    choice = random.randint(0,2)
    return utils.convert_to_name(choice)

def rock_or_paper(my_moves, opponent_moves):
    choice = random.randint(0,1)
    return utils.convert_to_name(choice)

def rock_only(my_moves, opponent_moves):
    return 'rock'

def paper_only(my_moves, opponent_moves):
    return 'paper'

def scissors_only(my_moves, opponent_moves):
    return 'scissors'

def example_strategy(my_moves, opponent_moves):
    # Author: Joe
    if opponent_moves:
        return opponent_moves[-1]
    else:
        return 'rock'