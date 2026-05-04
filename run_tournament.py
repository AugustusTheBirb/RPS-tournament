import numpy as np
import pandas as pd
import strategies
from utils import *
import inspect

def game(length, strategy1, strategy2):
    move_list = ['rock', 'paper', 'scissors']
    strategy1_moves = np.empty(length, dtype=object)
    strategy2_moves = np.empty(length, dtype=object)
    strategy1_score = 0
    strategy2_score = 0
    matrix = [[(0,0),(-1,1),(1,-1)],
              [(1,-1),(0,0),(-1,1)],
              [(-1,1),(1,-1),(0,0)]]
    #    R    P    S
    # R 0,0  -1,1  1,-1
    # P 1,-1  0,0  -1,1
    # S -1,1  1,-1  0,0
    for i in range(length):
        choice1 = strategy1(strategy1_moves[:i], strategy2_moves[:i])
        choice2 = strategy2(strategy2_moves[:i], strategy1_moves[:i])

        if choice1 not in move_list:
            raise ValueError("\"" + strategy1.__name__ + "\" submitted invalid move: "
                             + choice1)
        if choice2 not in move_list:
            raise ValueError("\"" + strategy2.__name__ + "\" submitted invalid move: "
                             + choice2)
        result = matrix[convert_to_id(choice1)][convert_to_id(choice2)]
        strategy1_score += result[0]
        strategy2_score += result[1]
        strategy1_moves[i] = choice1
        strategy2_moves[i] = choice2

    return strategy1_score, strategy2_score

def tournament(strategy_list):
    K = 1000
    REPEATS = 3
    num_strategies = len(strategy_list)
    strategy_names = list(x.__name__ for x in strategy_list)
    tournament_results = np.zeros((num_strategies,num_strategies))
    for i in range(num_strategies):
        for j in range(i, num_strategies):
            if i == j: continue
            temp_1 = 0
            temp_2 = 0
            for _ in range(REPEATS):
                game_results = game(K, strategy_list[i], strategy_list[j])
                temp_1 += game_results[0]
                temp_2 += game_results[1]
            tournament_results[i][j] = temp_1/REPEATS
            tournament_results[j][i] = temp_2/REPEATS
    df_results = pd.DataFrame(tournament_results, columns=strategy_names,
                                 index=strategy_names)
    df_results['average_score'] = df_results.mean(axis=1)
    df_results = df_results.round(1)
    df_results.to_csv('last_run.csv')
    print(df_results)

if __name__ == '__main__':
    strats = [obj for name, obj in
              inspect.getmembers(strategies, inspect.isfunction)]
    tournament(strats)