# snake game with pygame
import pygame
import random
import snake_ai
import logging
import concurrent.futures

class Board:
    def __init__(self, width, height, screen, screen_size, move_limit, debug=False, does_draw=True):
        self.does_draw = does_draw
        self.move_limit = move_limit
        self.debug = debug
        self.width = width
        self.screen = screen
        self.height = height
        self.food = None
        self.direction = 'right'
        self.score = 0
        self.num_moves = 0
        self.scale = screen_size//max(width,height) - 10
        self.padding = self.scale//5
        self.action_queue = []
        self.game_over = False
        self.reset()

    def generate_food(self):
        for _ in range(self.width*self.height*100):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in self.snake:
                self.food = (x, y)
                return True
        if self.debug: logging.info("could not generate food")
        return False

    def move_snake(self):
        head = self.snake[0]
        if self.direction == 'right':
            new_head = (head[0] + 1, head[1])
        elif self.direction == 'left':
            new_head = (head[0] - 1, head[1])
        elif self.direction == 'up':
            new_head = (head[0], head[1] - 1)
        elif self.direction == 'down':
            new_head = (head[0], head[1] + 1)
        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            if not self.generate_food():
                self.win()
        else:
            self.snake.pop()

    def win(self):
        self.game_over = True
    
    def check_collision(self):
        head = self.snake[0]
        if head[0] < 0 or head[0] >= self.width:
            self.game_over = True
        if head[1] < 0 or head[1] >= self.height:
            self.game_over = True
        if head in self.snake[1:]:
            self.game_over = True
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (0, 0, 255), (self.snake[0][0] * self.scale + self.padding, self.snake[0][1] * self.scale + self.padding, self.scale - (self.padding), self.scale - (self.padding)))
        pygame.draw.rect(self.screen, (255, 255, 255), (self.snake[-1][0] * self.scale + self.padding, self.snake[-1][1] * self.scale + self.padding, self.scale - (self.padding), self.scale - (self.padding)))        
        redness = 255
        for x, y in self.snake[1:len(self.snake)-1]:
            redness = redness - 20 if redness-20 > 0 else 0
            pygame.draw.rect(self.screen, (redness, 255, 0), (x * self.scale + self.padding, y * self.scale + self.padding, self.scale - (self.padding), self.scale - (self.padding)))
        pygame.draw.rect(self.screen, (255, 0, 0), (self.food[0] * self.scale + self.padding, self.food[1] * self.scale + self.padding, self.scale - (self.padding), self.scale - (self.padding)))

        # draw score
        font = pygame.font.SysFont('Arial', 20)
        text = font.render('Score: ' + str(self.score), True, (255, 255, 255))
        self.screen.blit(text, (0, self.height * self.scale))
        
        # draw grid lines
        for x in range(self.width + 1):
            pygame.draw.line(screen, (255, 255, 255), (x * self.scale, 0), (x * self.scale, self.height * self.scale), 1)
        for y in range(self.height + 1):
            pygame.draw.line(screen, (255, 255, 255), (0, y * self.scale), (self.width * self.scale, y * self.scale), 1)
        pygame.display.flip()

        self.draw_heuristics()

        pygame.display.update()

    def draw_heuristics(self):
        font = pygame.font.SysFont('Arial', 20)
        text = font.render(f'num moves: {self.num_moves}', True, (255, 255, 255))
        self.screen.blit(text, (80, self.height * self.scale))
        pygame.display.flip()
    
    def handle_input(self, input):
        if input == 'right' and self.direction != 'left':
            self.direction = 'right'
        elif input == 'left' and self.direction != 'right':
            self.direction = 'left'
        elif input == 'up' and self.direction != 'down':
            self.direction = 'up'
        elif input == 'down' and self.direction != 'up':
            self.direction = 'down'
    
    def update(self):
        if self.debug: logging.info(f'updated: {self.num_moves} {self.direction}')
        self.move_snake()
        self.check_collision()
        if self.does_draw: self.draw()
        self.num_moves += 1
    
    def run_with_human_input(self):
        assert self.does_draw
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.action_queue.append('right')
                elif event.key == pygame.K_LEFT:
                    self.action_queue.append('left')
                elif event.key == pygame.K_UP:
                    self.action_queue.append('up')
                elif event.key == pygame.K_DOWN:
                    self.action_queue.append('down')
                elif event.key == pygame.K_SPACE:
                    self.reset()
        if len(self.action_queue) > 0:
            for action in self.action_queue:
                self.handle_input(action)
                self.update()
                pygame.time.delay(120)
            self.action_queue = []
        else:
            self.update()
            pygame.time.delay(120)
        if self.game_over:
            result = (self.score, self.num_moves)
            self.reset()
            return result
        
    def reset(self):
        if self.debug: logging.info('reset')
        self.snake = [(self.width // 2, self.height // 2)]
        tail = (self.snake[0][0] + 1, self.snake[0][1])
        self.snake.append(tail)
        # tail2 = (self.snake[0][0] + 2, self.snake[0][1])
        # self.snake.append(tail2)
        self.direction = 'right'
        self.score = len(self.snake)
        self.num_moves = 0
        self.game_over = False
        self.generate_food()
    
    def run_with_ai_input(self):
        if self.does_draw:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
        self.direction = snake_ai.get_action(self.snake, self.food, (self.width, self.height))
        if self.debug: logging.info(f'ai action: {self.direction}')
        if self.update() or self.num_moves > self.move_limit or self.game_over:
            to_return = (self.score, self.num_moves)
            if self.debug: logging.info(f'game over: {to_return}')
            self.reset()
            return to_return
        # pygame.time.delay(50)

def run_one_AI_game(name, board_size_x, board_size_y, screen, screen_size, max_moves, debug, does_draw):
    game = Board(board_size_x, board_size_y, screen, screen_size, max_moves, debug, does_draw)
    game.reset()
    result = False
    while not result:
        result = game.run_with_ai_input()
    print(f'Game {name} finished with score {result[0]} and {result[1]} moves')
    return result

if __name__ == '__main__':
    # things you might want to change
    # running_type = 'human'
    running_type = 'ai'
    does_draw = True
    num_games = 10

    board_size = 10
    max_moves = (board_size**3) * 2.3
    screen_size = 900

    result_log = []
    debug = snake_ai.debug
    if does_draw:
        pygame.init()
        screen = pygame.display.set_mode((screen_size, screen_size))
    else:
        screen = None

    if running_type == 'human':
        for i in range(num_games):
            board = Board(board_size, board_size, screen, screen_size, max_moves, debug, does_draw)
            result = False
            while not result:
                result = board.run_with_human_input()
            print(f'Game {i} finished with score {result[0]} and {result[1]} moves')
            result_log.append(result)
    elif running_type == 'ai' and not does_draw:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result_log = [executor.submit(run_one_AI_game, i, board_size, board_size, screen, screen_size, max_moves, debug, does_draw) for i in range(num_games)]
    elif running_type == 'ai' and does_draw:
        for i in range(num_games):
            result_log.append(run_one_AI_game(i, board_size, board_size, screen, screen_size, max_moves, debug, does_draw))
    else:
        raise Exception('unknown running type')

    total_score = 0
    total_moves = 0
    total_wins = 0
    max_score = float('-inf')
    min_score = float('inf')
    for result in result_log:
        if running_type == 'ai' and not does_draw: score, moves = result.result()
        else: score, moves = result
        if score == board_size**2:
            total_wins += 1
        total_score += score
        total_moves += moves
        if score > max_score:
            max_score = score
        if score < min_score:
            min_score = score
    print(f'average score: {total_score / num_games}')
    print(f'average moves: {total_moves / num_games}')
    print(f'max score: {max_score}')
    print(f'min score: {min_score}')
    print(f'win %: {total_wins / num_games}')
    pygame.quit()