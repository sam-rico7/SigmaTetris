import pygame
import random

colors = [
    (0, 128, 255),
    (0, 255, 0),
    (255, 255, 0),
    (255, 102, 0),
    (255, 0, 0),
    (0, 255, 255),
    (255, 0, 255),
]

class Figure:
    x = 0
    y = 0
    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(self.figures) - 1)
        self.color = random.randint(1, len(colors) - 1)
        self.rotation = 0

    def image(self):
        return self.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation - 1) % len(self.figures[self.type])

class Tetris:
    def __init__(self, height, width):
        self.level = 2
        self.score = 0
        self.state = "start"
        self.field = []
        self.height = 0
        self.width = 0
        self.zoom = 40
        self.figure = None
        self.next_figure = Figure(3, 0)
        self.high_score = self.load_high_score()
        self.height = height
        self.width = width
        self.field = []
        self.score = 0
        self.state = "start"
        screen_width, screen_height = pygame.display.get_surface().get_size()
        self.x = (screen_width - self.width * self.zoom) // 2
        self.y = (screen_height - self.height * self.zoom) // 2
        for i in range(height):
            new_line = []
            for j in range(width):
                new_line.append(0)
            self.field.append(new_line)

    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as file:
                content = file.read().strip()
                return int(content) if content else 0
        except FileNotFoundError:
            return 0

    def save_high_score(self):
        with open("highscore.txt", "w") as file:
            file.write(str(self.high_score))

    def new_figure(self):
        if self.next_figure is None:
            self.next_figure = Figure(3, 0)
        self.figure = self.next_figure
        self.next_figure = Figure(3, 0)

    def get_next_figure(self):
        return self.next_figure

    def intersects(self):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if (
                        i + self.figure.y > self.height - 1
                        or j + self.figure.x > self.width - 1
                        or j + self.figure.x < 0
                        or self.field[i + self.figure.y][j + self.figure.x] > 0
                    ):
                        intersection = True
        return intersection

    def reset(self):
        self.__init__(self.height, self.width)

    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1 - 1][j]
        self.score += lines ** 2

        if self.score // 10 > (self.score - lines ** 2) // 10:
            self.level += 1
            self.update_speed()
    
    def update_speed(self):
        self.move_delay = max(1, 15 - self.level)
        self.speed_multiplier = min(self.level / 4, max_speed)

    def go_space(self):
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def go_down(self):
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.break_lines()
        self.new_figure()
        if self.intersects():
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            self.state = "gameover"

    def go_side(self, dx):
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x

    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation


pygame.init()

BLACK = (0, 0, 0)
GRAY = (0, 81, 105)
NEON_GREEN = (0, 255, 0)
NEON_PINK = (255, 0, 255)
NEON_BLUE = (0, 0, 255)

size = (800, 1000)
screen = pygame.display.set_mode(size)

done = False
clock = pygame.time.Clock()
fps = 30
game = Tetris(18, 10)
counter = 0

pygame.display.set_caption("Tetris")

pressing_down = False
retro_font_large = pygame.font.Font(pygame.font.match_font("Retro"), 130)
retro_font_small = pygame.font.Font(pygame.font.match_font("Retro"), 50)

move_timer = 0
move_delay = 3
moving_left = False
moving_right = False
speed_multiplier = 1
max_speed = 5

while not done:
    if game.figure is None:
        game.new_figure()
    counter += 1

    if counter > 100000:
        counter = 0

    if counter % (fps // game.level // 1.5) == 0 or pressing_down:
        if game.state == "start":
            game.go_down()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                game.figure.rotate()
                pressing_down = False

            if event.key == pygame.K_DOWN:
                pressing_down = True

            if event.key == pygame.K_LEFT:
                moving_left = True

            if event.key == pygame.K_RIGHT:
                moving_right = True

            if event.key == pygame.K_SPACE:
                game.go_space()
                pressing_down = False

            if event.key == pygame.K_ESCAPE:
                game.reset()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                pressing_down = False
            if event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_RIGHT:
                moving_right = False

    if moving_left:
        speed_multiplier += 0.01
    if moving_right:
        speed_multiplier += 0.01

    speed_multiplier = min(speed_multiplier, max_speed)
    move_delay = max(1, int(15/speed_multiplier))

    if moving_left and move_timer == 0:
        game.go_side(-1)
        move_timer = move_delay
    if moving_right and move_timer == 0:
        game.go_side(1)
        move_timer = move_delay

    if move_timer > 0:
        move_timer -= 1
    screen.fill(BLACK)

    pygame.draw.rect(
        screen,
        NEON_BLUE,
        [game.x - 10, game.y - 10, game.zoom * game.width + 20, game.zoom * game.height + 20],
        10,
    )

    for i in range(game.height):
        for j in range(game.width):
            pygame.draw.rect(
                screen,
                GRAY,
                [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom],
                2,
            )
            if game.field[i][j] > 0:
                pygame.draw.rect(
                    screen,
                    colors[game.field[i][j]],
                    [game.x + game.zoom * j + 2, game.y + game.zoom * i + 2, game.zoom - 4, game.zoom - 4],
                )

    if game.figure is not None:
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in game.figure.image():
                    pygame.draw.rect(
                        screen,
                        colors[game.figure.color],
                        [
                            game.x + game.zoom * (j + game.figure.x) + 2,
                            game.y + game.zoom * (i + game.figure.y) + 2,
                            game.zoom - 4,
                            game.zoom - 4,
                        ],
                    )

    next_figure = game.get_next_figure()
    for i in range(4):
        for j in range(4):
            p = i * 4 + j
            if p in next_figure.image():
                pygame.draw.rect(
                    screen,
                    colors[next_figure.color],
                    [
                        game.x + game.zoom * (j + 10.5) + 2,
                        game.y + game.zoom * (i + 1) + 2,
                        game.zoom - 4,
                        game.zoom - 4,
                    ],
                )

    text_score = retro_font_small.render(f"Score: {game.score}", True, NEON_GREEN)
    text_high_score = retro_font_small.render(f"High Score: {game.high_score}", True, NEON_PINK)
    text_game_over = retro_font_large.render("GAME OVER", True, (200, 0, 200))
    text_press_esc = retro_font_small.render("Press ESC to Restart", True, NEON_BLUE)
    text_next = retro_font_small.render("Next", True, NEON_GREEN)

    screen.blit(text_score, [20, 20])
    screen.blit(text_high_score, [20, 80])
    screen.blit(text_next, [660, 80])
    if game.state == "gameover":
        screen.blit(text_game_over, [150, 400])
        screen.blit(text_press_esc, [245, 900])

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
print(f"High Score: {game.high_score}")