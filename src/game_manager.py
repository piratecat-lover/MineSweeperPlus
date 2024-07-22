import pygame
import sys
from game_functions import Board, GameContainer
from io_settings import load_sprites, settings

# Initialize Pygame
pygame.init()
font = pygame.font.Font(None, settings['font_size'])

class GameScreenManager:
    def __init__(self, difficulty, player_name="Player"):
        self.board = Board(*settings['game_settings'][difficulty])
        self.game_container = GameContainer(difficulty, player_name)
        self.difficulty = difficulty
        self.player_name = player_name
        self.running = True
        
        self.TILESIZE = 32
        self.HEADERSIZE = 60
        self.SCREEN_WIDTH = self.board.cols * self.TILESIZE
        self.SCREEN_HEIGHT = self.board.rows * self.TILESIZE + self.HEADERSIZE
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.sprites = load_sprites(settings)
        
        pygame.display.set_caption("Minesweeper")
        self.clock = pygame.time.Clock()

    def display(self):
        self.screen.fill(settings['colors']['white'])
        self.draw_board()
        self.draw_header()

        pygame.display.flip()
        self.clock.tick(settings['fps'])

    def draw_board(self):
        for row in self.board.board_list:
            for tile in row:
                x, y = tile.x * self.TILESIZE, tile.y * self.TILESIZE + self.HEADERSIZE
                if tile.revealed:
                    if tile.type == "X":
                        self.screen.blit(self.sprites["exploded"], (x, y))
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

    def draw_header(self):
        pygame.draw.rect(self.screen, settings['colors']['gray'], (0, 0, self.SCREEN_WIDTH, self.HEADERSIZE))
        elapsed_time = (pygame.time.get_ticks() - self.game_container.start_time) // 1000
        flags_text = font.render(f"Flags: {self.board.flags}/{self.board.mines}", True, settings['colors']['black'])
        time_text = font.render(f"Time: {elapsed_time}s", True, settings['colors']['black'])
        self.screen.blit(flags_text, (10, 10))
        self.screen.blit(time_text, (self.SCREEN_WIDTH - 150, 10))
        
        # Display player avatar
        avatar = self.sprites['doa'][0 if not self.game_container.game_over else 1]
        avatar = pygame.transform.scale(avatar, (self.HEADERSIZE - 10, self.HEADERSIZE - 10))
        avatar_rect = avatar.get_rect(center=(self.SCREEN_WIDTH // 2, self.HEADERSIZE // 2))
        self.screen.blit(avatar, avatar_rect)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.save_and_quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.left_click(event.pos)
            elif event.button == 3:  # Right click
                self.right_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.save_and_quit()

    def left_click(self, pos):
        x = pos[0] // self.TILESIZE
        # y = (pos[1]) // self.TILESIZE
        y = (pos[1] - self.HEADERSIZE) // self.TILESIZE
        if 0 <= x < self.board.cols and 0 <= y < self.board.rows:
            result = self.board.left_click(x, y)
            if result == "Game Over":
                self.game_container.game_over = True
                self.display_game_over()
            if self.check_win():
                self.game_container.win = True
                self.display_win()

    def right_click(self, pos):
        x = pos[0] // self.TILESIZE
        # y = (pos[1]) // self.TILESIZE
        y = (pos[1] - self.HEADERSIZE) // self.TILESIZE
        if 0 <= x < self.board.cols and 0 <= y < self.board.rows:
            self.board.right_click(x, y)

    def display_game_over(self):
        game_over_text = font.render("Game Over", True, settings['colors']['black'])
        self.screen.blit(game_over_text, (self.SCREEN_WIDTH // 2 - 50, self.SCREEN_HEIGHT // 2))
        pygame.display.flip()
        self.game_container.update_match_record('lost')
        self.game_container.delete_save_game()
        pygame.time.wait(2000)
        self.running = False

    def display_win(self):
        win_text = font.render("You Win!", True, settings['colors']['black'])
        self.screen.blit(win_text, (self.SCREEN_WIDTH // 2 - 50, self.SCREEN_HEIGHT // 2))
        pygame.display.flip()
        self.game_container.update_match_record('won')
        self.game_container.add_to_leaderboard()
        self.game_container.delete_save_game()
        pygame.time.wait(2000)
        self.running = False

    def check_win(self):
        for row in self.board.board_list:
            for tile in row:
                if tile.type != "X" and not tile.revealed:
                    return False
        return True

    def save_and_quit(self):
        self.game_container.save_game_state(self.board)
        pygame.quit()
        sys.exit()