# game_manager.py

import pygame
import sys
from game_functions import GameContainer, Board
from io_settings import load_json

def load_sprites(settings):
    sprites = {}
    for key, path in settings['sprites'].items():
        if isinstance(path, list):
            sprites[key] = [pygame.transform.scale(pygame.image.load(p), (32, 32)) for p in path]
        else:
            sprites[key] = pygame.transform.scale(pygame.image.load(path), (32, 32))
    return sprites

class DisplayBoard(Board):
    def __init__(self, rows, cols, mines):
        super().__init__(rows, cols, mines)
        self.settings = load_json("settings")
        self.sprites = load_sprites(self.settings)
        self.TILESIZE = 32
        self.HEADERSIZE = 60
        super().new_game()
        self.SCREEN_WIDTH = self.cols * self.TILESIZE
        self.SCREEN_HEIGHT = self.rows * self.TILESIZE + self.HEADERSIZE
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.font = pygame.font.Font(None, self.settings['font_size'])
        pygame.display.set_caption("Minesweeper++")
        self.clock = pygame.time.Clock()

    def display(self):
        self.draw_board()
        pygame.display.flip()
        self.clock.tick(self.settings['fps'])

    def draw_board(self):
        for row in self.board_list:
            for tile in row:
                x, y = tile.x * self.TILESIZE, tile.y * self.TILESIZE + self.HEADERSIZE
                if tile.revealed:
                    if tile.type == "X":
                        self.screen.blit(self.sprites["mine"], (x, y))
                    elif tile.type.startswith("C"):
                        num = int(tile.type[1:])
                        self.screen.blit(self.sprites["numbers"][num], (x, y))
                    else:
                        self.screen.blit(self.sprites["numbers"][0], (x, y))
                else:
                    if tile.flagged:
                        self.screen.blit(self.sprites["flag"], (x, y))
                    else:
                        self.screen.blit(self.sprites["covered"], (x, y))

    def reset_board(self, elapsed_time, mode="ratio"):
        self.display_reset_popup()
        super().reset_board(elapsed_time, mode)

    def display_reset_popup(self):
        popup_text = self.font.render("Board is resetting...", True, self.settings['colors']['black'])
        popup_rect = popup_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2))
        self.screen.blit(popup_text, popup_rect)
        pygame.display.flip()
        pygame.time.wait(1000)

class DisplayGameContainer(GameContainer):
    def __init__(self, difficulty):
        super().__init__(difficulty)
        self.dboard = DisplayBoard(*self.settings['game_settings'][self.difficulty])
        self.start_game(pygame.time.get_ticks())
    
    def draw_header(self):
        pygame.draw.rect(self.dboard.screen, self.settings['colors']['gray'], (0, 0, self.dboard.SCREEN_WIDTH, 60))
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000

        if self.difficulty == "adventure":
            time_left = max(0, 300 - elapsed_time)
            minutes, seconds = divmod(time_left, 60)
            time_text = f"Time Left: {minutes:02}:{seconds:02}"
        else:
            minutes, seconds = divmod(elapsed_time, 60)
            time_text = f"Elapsed Time: {minutes:02}:{seconds:02}"
        
        time_text_rendered = self.dboard.font.render(time_text, True, self.settings['colors']['black'])
        mine_count_text = self.dboard.font.render(f"{self.dboard.guess_mines}", True, self.settings['colors']['black'])
        
        self.dboard.screen.blit(time_text_rendered, (10, 10))
        self.dboard.screen.blit(self.dboard.sprites["mine"], (self.dboard.SCREEN_WIDTH // 2 - 16, 10))
        self.dboard.screen.blit(mine_count_text, (self.dboard.SCREEN_WIDTH // 2 + 20, 10))
    
    def display(self):
        self.dboard.screen.fill(self.settings['colors']['white'])
        self.draw_header()
        self.dboard.display()
    
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.save_game_state()
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x = event.pos[0] // self.dboard.TILESIZE
            y = (event.pos[1] - self.dboard.HEADERSIZE) // self.dboard.TILESIZE
            if 0 <= x < self.dboard.cols and 0 <= y < self.dboard.rows:
                if event.button == 1:  # Left click
                    result = self.dboard.left_click(x, y)
                    if result == "Game Over":
                        self.dboard.game_over = True
                        self.display_game_over()
                    elif self.dboard.valid_clicks >= 10:
                        self.dboard.reset_board((pygame.time.get_ticks() - self.start_time) // 1000, "ratio")
                    elif self.dboard.check_win():
                        self.dboard.game_over = True
                        self.display_win()
                elif event.button == 3:  # Right click
                    self.dboard.right_click(x, y)
                elif event.button == 2:  # Middle click (Mouse wheel button)
                    if not self.dboard.board_list[x][y].flagged:  # Prevent middle click from revealing flagged tiles
                        self.dboard.middle_click(x, y)
    
    def display_game_over(self):
        game_over_text = self.dboard.font.render("Game Over", True, self.dboard.settings['colors']['black'])
        self.dboard.screen.blit(game_over_text, (self.dboard.SCREEN_WIDTH // 2 - 50, self.dboard.SCREEN_HEIGHT // 2))
        pygame.display.flip()
        self.update_match_record(False)
        self.delete_save_game()
        pygame.time.wait(2000)

    def display_win(self):
        win_text = self.dboard.font.render("You Win!", True, self.dboard.settings['colors']['black'])
        self.dboard.screen.blit(win_text, (self.dboard.SCREEN_WIDTH // 2 - 50, self.dboard.SCREEN_HEIGHT // 2))
        pygame.display.flip()
        self.update_match_record(True)
        self.add_to_leaderboard("Player", (pygame.time.get_ticks() - self.start_time) // 1000)
        self.delete_save_game()
        pygame.time.wait(2000)
