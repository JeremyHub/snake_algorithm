import snake
import pygame
import concurrent.futures
import plotille

debug = False

if __name__ == '__main__':

    # things you might want to change

    # running_type = 'human'
    running_type = 'ai'
    # running_type = 'debug_ai'
    does_draw = False
    num_games = 1000
    board_size = 10

    max_moves = (board_size**3.36)
    screen_size = 900

    result_log = []
    if does_draw or running_type == 'debug_ai':
        pygame.init()
        screen = pygame.display.set_mode((screen_size, screen_size))
    else:
        screen = None

    if running_type == 'human':
        for i in range(num_games):
            board = snake.Board(board_size, board_size, screen, screen_size, max_moves, debug, does_draw)
            result = False
            while not result:
                result = board.run_with_human_input()
            print(f'Game {i} finished with score {result[0]} and {result[1]} moves')
            result_log.append(result)
    elif running_type == 'ai' and not does_draw and not debug:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            result_log = [executor.submit(snake.run_one_AI_game, i, board_size, board_size, screen, screen_size, max_moves, debug, does_draw) for i in range(num_games)]
    elif running_type == 'ai' and (does_draw or debug):
        for i in range(num_games):
            result_log.append(snake.run_one_AI_game(i, board_size, board_size, screen, screen_size, max_moves, debug, does_draw))
    elif running_type == 'debug_ai':
        for i in range(num_games):
            game = snake.Board(board_size, board_size, screen, screen_size, max_moves, debug, does_draw, True)
            result = False
            while not result:
                result = game.run_with_ai_input()
            if result[0] < 20:
                foods = game.foods
                moves = game.moves
                while True:
                    game.reconstruct_game(moves.copy(), foods.copy())
            else:
                print(f'Game {i} finished with score {result[0]} and {result[1]} moves')
    else:
        raise Exception('unknown running type')

    total_score = 0
    total_moves = 0
    total_wins = 0
    max_score = float('-inf')
    min_score = float('inf')
    all_moves = []
    scores = []
    for result in result_log:
        if running_type == 'ai' and not (does_draw or debug): score, moves = result.result()
        else: score, moves = result
        all_moves.append(moves)
        scores.append(score)
        if score == board_size**2:
            total_wins += 1
        total_score += score
        total_moves += moves
        if score > max_score:
            max_score = score
        if score < min_score:
            min_score = score

    fig = plotille.Figure()
    fig.width = 60
    fig.height = 30
    fig.color_mode = 'byte'
    fig.histogram(all_moves, bins=100)
    print(fig.show(legend=True))

    fig2 = plotille.Figure()
    fig2.width = 60
    fig2.height = 30
    fig2.color_mode = 'byte'
    fig2.histogram(scores, bins=100)
    print(fig2.show(legend=True))

    print(f'average score: {total_score / num_games}')
    print(f'average moves: {total_moves / num_games}')
    print(f'max score: {max_score}')
    print(f'min score: {min_score}')
    print(f'win %: {total_wins / num_games}')
    pygame.quit()