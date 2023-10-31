import os
import pygame
import random
import sys
import time

from pygame.math import Vector2

# Set the colors
COLOUR_BG = (175, 215, 70)
COLOUR_FRUIT = (183, 111, 122)
COLOUR_SNAKE = (126, 166, 114)

# Set the constants
CELL_SIZE, CELL_NUMBER = 30, 20
SCREEN_WIDTH = CELL_SIZE * CELL_NUMBER
SCREEN_HEIGHT = CELL_SIZE * CELL_NUMBER

# Initialize Pygame
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# Set the timer (reflect the snake speed)
pygame.time.set_timer(pygame.USEREVENT, 100)

# Set the display
canva = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
canva.fill((0, 191, 255))  # deepskyblue

# Get the package base path
package_base_path = os.path.dirname(os.path.abspath(__file__))


def load_image(filename):
    return pygame.image.load(
        os.path.join(package_base_path, "Assets", "Graphics", filename)
    ).convert_alpha()


def load_sound(filename):
    return pygame.mixer.Sound(
        os.path.join(package_base_path, "Assets", "Sound", filename)
    )


fruit_graphic = load_image("apple.png")
head_up_graphic = load_image("head_up.png")
head_down_graphic = load_image("head_down.png")
head_right_graphic = load_image("head_right.png")
head_left_graphic = load_image("head_left.png")
tail_up_graphic = load_image("tail_up.png")
tail_down_graphic = load_image("tail_down.png")
tail_right_graphic = load_image("tail_right.png")
tail_left_graphic = load_image("tail_left.png")
body_vertical_graphic = load_image("body_vertical.png")
body_horizontal_graphic = load_image("body_horizontal.png")
body_tr_graphic = load_image("body_tr.png")
body_tl_graphic = load_image("body_tl.png")
body_br_graphic = load_image("body_br.png")
body_bl_graphic = load_image("body_bl.png")
crunch_sound_graphic = load_sound("crunch.wav")

"""
A fruit object should have x and y coordinates.
When the snake's head matches its position, the fruit should be randomly placed, ensuring it does not overlap with the snake's body.
"""


class Fruit:
    def __init__(self):
        self.random_place()

    def random_place(self):
        self.pos = Vector2(
            random.choice(range(CELL_NUMBER)), random.choice(range(CELL_NUMBER))
        )

    def draw(self):
        canva.blit(
            fruit_graphic,
            pygame.Rect(
                self.pos.x * CELL_SIZE,
                self.pos.y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            ),
        )


"""
A snake object should have x and y coordinates.
It can move, grow, and play sound.
"""


class Snake:
    def __init__(self):
        self.body = [Vector2(5, 10), Vector2(6, 10), Vector2(7, 10)]
        self.direction = Vector2(0, 0)
        self.add_body = False
        self.crunch_sound_graphic = crunch_sound_graphic
        self.head_graphic = head_right_graphic
        self.tail_graphic = tail_right_graphic
        self.body_vertical_graphic = body_vertical_graphic
        self.body_horizontal_graphic = body_horizontal_graphic
        self.body_tl_graphic = body_tl_graphic
        self.body_bl_graphic = body_bl_graphic
        self.body_br_graphic = body_br_graphic
        self.body_tr_graphic = body_tr_graphic

    @property
    def head(self):
        return self.body[-1]

    @property
    def tail(self):
        return self.body[0]

    @property
    def length(self):
        return len(self.body)

    def play_sound(self):
        self.crunch_sound_graphic.play()

    def draw(self):
        self.__update_head_graphic()
        self.__update_tail_graphic()
        self.__draw_body()

    def __draw_body(self):
        for index, block in enumerate(self.body):
            block_rect = pygame.Rect(
                block.x * CELL_SIZE, block.y * CELL_SIZE, CELL_SIZE, CELL_SIZE
            )
            if index == 0:
                canva.blit(self.tail_graphic, block_rect)
            elif index == self.length - 1:
                canva.blit(self.head_graphic, block_rect)
            else:
                prev_block = self.body[index - 1] - block
                next_block = self.body[index + 1] - block
                graphic = self.__choose_graphic(prev_block, next_block)
                if graphic != None:
                    canva.blit(graphic, block_rect)

    def __choose_graphic(self, prev_block, next_block):
        if prev_block.x == next_block.x:
            return self.body_vertical_graphic
        elif prev_block.y == next_block.y:
            return self.body_horizontal_graphic
        elif (
            prev_block.x == -1
            and next_block.y == -1
            or prev_block.y == -1
            and next_block.x == -1
        ):
            return self.body_tl_graphic
        elif (
            prev_block.x == -1
            and next_block.y == 1
            or prev_block.y == 1
            and next_block.x == -1
        ):
            return self.body_bl_graphic
        elif (
            prev_block.x == 1
            and next_block.y == -1
            or prev_block.y == -1
            and next_block.x == 1
        ):
            return self.body_tr_graphic
        elif (
            prev_block.x == 1
            and next_block.y == 1
            or prev_block.y == 1
            and next_block.x == 1
        ):
            return self.body_br_graphic

    def __update_tail_graphic(self):
        tail_direction = self.body[1] - self.tail
        if tail_direction == Vector2(1, 0):
            self.tail_graphic = tail_left_graphic
        elif tail_direction == Vector2(-1, 0):
            self.tail_graphic = tail_right_graphic
        elif tail_direction == Vector2(0, 1):
            self.tail_graphic = tail_up_graphic
        elif tail_direction == Vector2(0, -1):
            self.tail_graphic = tail_down_graphic

    def __update_head_graphic(self):
        head_direction = self.head - self.body[-2]
        if head_direction == Vector2(1, 0):
            self.head_graphic = head_right_graphic
        elif head_direction == Vector2(-1, 0):
            self.head_graphic = head_left_graphic
        elif head_direction == Vector2(0, 1):
            self.head_graphic = head_down_graphic
        elif head_direction == Vector2(0, -1):
            self.head_graphic = head_up_graphic

    def move(self):
        if self.add_body:
            self.body.insert(0, self.tail - (self.body[1] - self.tail))
            self.add_body = False
        elif self.direction != Vector2(0, 0):
            self.body = self.body[1:] + [self.head + self.direction]

    def grow(self):
        self.add_body = True


"""
SnakeGame() takes advantage of fruit() and Snake().
It defines the game logic and reflects OOP features in Python.
"""


class SnakeGame:
    def __init__(self):
        self.fruit = Fruit()
        self.snake = Snake()
        while self.fruit.pos in self.snake.body:
            self.fruit.random_place()

    def draw(self):
        self.__draw_score()
        self.fruit.draw()
        self.snake.draw()

    def update(self):
        self.snake.move()
        self.__check_fruit_eaten()
        self.__check_fail()

    def __check_fruit_eaten(self):
        if self.fruit.pos == self.snake.head:
            self.snake.play_sound()
            self.snake.grow()
            self.fruit.random_place()
            while self.fruit.pos in self.snake.body:
                self.fruit.random_place()

    def __draw_score(self):
        score_surface = pygame.font.Font(
            os.path.join(
                package_base_path, "Assets", "Font", "PoetsenOne-Regular.ttf"
            ),
            25,
        ).render(f"Count: {str(self.snake.length - 3)}", True, (56, 74, 12))
        canva.blit(
            score_surface,
            score_surface.get_rect(
                center=(
                    int(CELL_NUMBER * CELL_SIZE - 60),
                    int(CELL_NUMBER * CELL_SIZE - 40),
                )
            ),
        )

    def __check_fail(self):
        if (
            not 0 <= self.snake.head.x < CELL_NUMBER
            or not 0 <= self.snake.head.y < CELL_NUMBER
            or any(
                segment == self.snake.head for segment in self.snake.body[:-1]
            )  # An easy way to judge whether the snake hits its own body or not
        ):
            self.__game_over()

    def __game_over(self):
        gameover_color = pygame.font.SysFont(
            "skia", 40, bold=True, italic=True
        ).render("Game Over", True, pygame.Color(153, 0, 0))
        gameover_location = gameover_color.get_rect(
            midtop=(int(CELL_SIZE * CELL_NUMBER / 2), 20)
        )
        canva.blit(gameover_color, gameover_location)
        pygame.display.flip()
        while True:
            SnakeGame.welcome("Restart")
            SnakeGame.new_game()

    @staticmethod
    def __close_game():
        pygame.quit()
        sys.exit()

    @staticmethod
    def welcome(msg):
        text = pygame.font.Font(None, 100).render(msg, True, (0, 0, 0))
        text_rect = text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )
        pygame.draw.rect(canva, (255, 255, 0), text_rect)
        canva.blit(text, text_rect)
        pygame.display.flip()

        while True:
            clock.tick(
                50
            )  # avoid the program from using too much CPU resources (30~60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    SnakeGame.__close_game()
                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and text_rect.collidepoint(event.pos)
                ):
                    return

    @staticmethod
    def new_game():
        snake_game = SnakeGame()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    snake_game.__close_game()
                elif event.type == pygame.USEREVENT:
                    snake_game.update()
                elif event.type == pygame.KEYDOWN:
                    if (
                        event.key == pygame.K_UP
                        and snake_game.snake.direction != Vector2(0, 1)
                    ):
                        snake_game.snake.direction = Vector2(0, -1)
                    elif (
                        event.key == pygame.K_DOWN
                        and snake_game.snake.direction != Vector2(0, -1)
                    ):
                        snake_game.snake.direction = Vector2(0, 1)
                    elif (
                        event.key == pygame.K_LEFT
                        and snake_game.snake.direction != Vector2(1, 0)
                        and snake_game.snake.direction != Vector2(0, 0)
                    ):
                        snake_game.snake.direction = Vector2(-1, 0)
                    elif (
                        event.key == pygame.K_RIGHT
                        and snake_game.snake.direction != Vector2(-1, 0)
                    ):
                        snake_game.snake.direction = Vector2(1, 0)
            pygame.display.set_caption(f"PYGAME {time.ctime()[11:19]}")
            canva.fill(COLOUR_BG)
            clock.tick(60)
            snake_game.draw()
            pygame.display.update()


SnakeGame.welcome("Start_Game")
SnakeGame.new_game()
