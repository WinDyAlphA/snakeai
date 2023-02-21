import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

BLOCK_SIZE = 20
SPEED = 150

class SnakeGameAI:

    def __init__(self, w=400, h=400):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()
        
        


    def reset(self):
        # init game state
        self.direction = Direction.RIGHT
        self.matrice = False*np.ones((self.w//BLOCK_SIZE,self.h//BLOCK_SIZE))
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0
        self.corpsU = True
        self.corpsL = True
        self.moves = 0
        self.best_moves = abs(self.food.y - self.head.y)/BLOCK_SIZE + abs(self.food.x - self.head.x)/BLOCK_SIZE


    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()
        
    #creer une matrice de 20x20 qui repsente la grille de jue, le serpent est True, le reste est False
    def matrice(self):
        matrice = np.zeros((20,20))
        for i in range(20):
            for j in range(20):
                if Point(i*20,j*20) in self.snake:
                    matrice[i][j] = True
                else:
                    matrice[i][j] = False
        return matrice

    def log_mapping(self,x):
        if x < 0:
            return 0
        if x == 0:
            return 1
        return int(np.log(x)/np.log(2)) + 1



    
    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move
        self.moves += 1
        self._move(action) # update the head
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        reward = -0.1
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score
        # 4. place new food or just move
        if self.head == self.food:
            ways = self.moves - self.best_moves
            
            self.moves = 0
            self.score += 1
            reward = 17 - self.log_mapping((self.moves - self.best_moves))
            self._place_food()
            x = abs(self.food.x - self.head.x)/BLOCK_SIZE
            y = abs(self.food.y - self.head.y)/BLOCK_SIZE
            self.best_moves = x+y
             

        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.update_corps()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, self.score


    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False

    def update_corps(self):
        corpsUp,corpsDown,corpsRight,corpsLeft = 0,0,0,0
        for pt in self.snake:
            if pt.x > self.head.x:
                corpsRight += 1
            elif pt.x < self.head.x:
                corpsLeft += 1
            elif pt.y > self.head.y:
                corpsDown += 1
            elif pt.y < self.head.y:
                corpsUp += 1

        if corpsUp > corpsDown:
            self.corpsU = True
        else:
            self.corpsU = False
        if corpsLeft > corpsRight:
            self.corpsL = True
        else:
            self.corpsL = False


    def _update_ui(self):
        self.display.fill((0,0,0))

        for pt in self.snake:
            pygame.draw.rect(self.display, (74,199,72), pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))

        pygame.draw.rect(self.display, (170,20,20), pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, (255,255,255))
        self.display.blit(text, [0, 0])
        pygame.display.flip()


    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)