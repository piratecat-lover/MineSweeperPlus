import pygame
import sys
import time  # Make sure to import the time module
from settings import *
from sprites import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((TITLE_WIDTH, TITLE_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 24)
        self.running = True
        self.board = None  # Initialize the board attribute
        self.board_size = '8x8'
        self.start_screen()

    def start_screen(self):
        self.screen = pygame.display.set_mode((TITLE_WIDTH, TITLE_HEIGHT))
        while True:
            self.screen.fill(BGCOLOUR)
            self.draw_text("Minesweeper", 48, TITLE_WIDTH // 2, TITLE_HEIGHT // 4)
            self.draw_text("New Game", 36, TITLE_WIDTH // 2, TITLE_HEIGHT // 2)
            self.draw_text("Continue", 36, TITLE_WIDTH // 2, TITLE_HEIGHT // 2 + 50)
            self.draw_text("Leaderboard", 36, TITLE_WIDTH // 2, TITLE_HEIGHT // 2 + 100)
            self.draw_text("Exit", 36, TITLE_WIDTH // 2, TITLE_HEIGHT // 2 + 150)
            pygame.display.flip()
            self.check_menu_events()

    def check_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if self.is_over_button(mx, my, TITLE_WIDTH // 2, TITLE_HEIGHT // 2):
                    self.new_game()
                elif self.is_over_button(mx, my, TITLE_WIDTH // 2, TITLE_HEIGHT // 2 + 50):
                    if self.board is not None:
                        self.run()
                elif self.is_over_button(mx, my, TITLE_WIDTH // 2, TITLE_HEIGHT // 2 + 100):
                    self.show_leaderboard()
                elif self.is_over_button(mx, my, TITLE_WIDTH // 2, TITLE_HEIGHT // 2 + 150):
                    self.quit_game()

    def is_over_button(self, mx, my, x, y):
        button_width, button_height = 200, 50
        return x - button_width // 2 <= mx <= x + button_width // 2 and y - button_height // 2 <= my <= y + button_height // 2

    def new_game(self):
        self.select_board_size()
        self.board = Board()  # Create a new Board object
        self.run()

    def select_board_size(self):
            while True:
                self.screen.fill(BGCOLOUR)
                self.draw_text("Select Board Size", 48, TITLE_WIDTH // 2, TITLE_HEIGHT // 4)
                self.draw_text("8x8 (10 mines)", 36, TITLE_WIDTH // 2, TITLE_HEIGHT // 2)
                self.draw_text("16x16 (40 mines)", 36, TITLE_WIDTH // 2, TITLE_HEIGHT // 2 + 50)
                self.draw_text("30x16 (99 mines)", 36, TITLE_WIDTH // 2, TITLE_HEIGHT // 2 + 100)
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit_game()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = pygame.mouse.get_pos()
                        if self.is_over_button(mx, my, TITLE_WIDTH // 2, TITLE_HEIGHT // 2):
                            self.board_size = '8x8'
                            self.update_settings('8x8')
                            return
                        elif self.is_over_button(mx, my, TITLE_WIDTH // 2, TITLE_HEIGHT // 2 + 50):
                            self.board_size = '16x16'
                            self.update_settings('16x16')
                            return
                        elif self.is_over_button(mx, my, TITLE_WIDTH // 2, TITLE_HEIGHT // 2 + 100):
                            self.board_size = '30x16'
                            self.update_settings('30x16')
                            return

    def update_settings(self, size_key):
        global ROWS, COLS, AMOUNT_MINES, WIDTH, HEIGHT
        ROWS, COLS, AMOUNT_MINES = BOARD_OPTIONS[size_key]
        WIDTH = TILESIZE * COLS
        HEIGHT = TILESIZE * ROWS + 50  # Extra space for banner
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

    def run(self):
        self.playing = True
        self.start_time = time.time()
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.draw()
        else:
            self.end_screen()

    def draw(self):
        self.screen.fill(BGCOLOUR)
        self.board.draw(self.screen)
        self.draw_banner()
        pygame.display.flip()

    def draw_banner(self):
        elapsed_time = int(time.time() - self.start_time)
        mines_left = AMOUNT_MINES - sum(tile.flagged for row in self.board.board_list for tile in row)
        self.draw_text(f'Time: {elapsed_time}', 24, 60, HEIGHT - 25)
        self.draw_text(f'Mines: {mines_left}', 24, WIDTH - 100, HEIGHT - 25)

    def draw_text(self, text, size, x, y):
        font = pygame.font.SysFont('arial', size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def check_win(self):
        for row in self.board.board_list:
            for tile in row:
                if tile.type != "X" and not tile.revealed:
                    return False
        return True

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                mx //= TILESIZE
                my //= TILESIZE

                if event.button == 1:
                    if not self.board.board_list[mx][my].flagged:
                        # dig and check if exploded
                        if not self.board.dig(mx, my):
                            # explode
                            for row in self.board.board_list:
                                for tile in row:
                                    if tile.flagged and tile.type != "X":
                                        tile.flagged = False
                                        tile.revealed = True
                                        tile.image = tile_not_mine
                                    elif tile.type == "X":
                                        tile.revealed = True
                            self.playing = False

                if event.button == 3:
                    if not self.board.board_list[mx][my].revealed:
                        self.board.board_list[mx][my].flagged = not self.board.board_list[mx][my].flagged

                if self.check_win():
                    self.win = True
                    self.playing = False
                    for row in self.board.board_list:
                        for tile in row:
                            if not tile.revealed:
                                tile.flagged = True

    def end_screen(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    return

    def show_leaderboard(self):
        self.screen = pygame.display.set_mode((TITLE_WIDTH, TITLE_HEIGHT))
        while True:
            self.screen.fill(BGCOLOUR)
            self.draw_text("Leaderboard", 48, TITLE_WIDTH // 2, TITLE_HEIGHT // 4)
            for i, (size, time) in enumerate(LEADERBOARD.items()):
                time_str = f"{time:.2f}" if time != float('inf') else "N/A"
                self.draw_text(f"{size}: {time_str} seconds", 36, TITLE_WIDTH // 2, TITLE_HEIGHT // 2 + i * 50)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return

    def quit_game(self):
        pygame.quit()
        sys.exit()


game = Game()
while game.running:
    game.start_screen()
