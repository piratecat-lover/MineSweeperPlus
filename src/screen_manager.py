import pygame
import sys
from io_settings import matchrecord, savedgame, save_json, load_sprites
from game_manager import GameScreenManager

class ScreenManager:
    def __init__(self, screen, font, settings, set_current_screen):
        self.screen = screen
        self.settings = settings
        self.font = font
        self.set_current_screen = set_current_screen
        self.sprites = load_sprites(self.settings)

    def draw_text(self, text, y_ratio, color):
        screen_width, screen_height = self.screen.get_size()
        y = int(screen_height * y_ratio)
        textobj = self.font.render(text, True, color)
        textrect = textobj.get_rect(center=(screen_width // 2, y))
        self.screen.blit(textobj, textrect)

    def save_and_quit(self):
        save_json("savedgame", savedgame)
        pygame.quit()
        sys.exit()

class TitleScreen(ScreenManager):
    def display(self):
        self.screen.fill(self.settings['colors']['white'])
        self.draw_text('Minesweeper', 0.1, self.settings['colors']['black'])
        self.draw_text('1. New Game', 0.2, self.settings['colors']['black'])
        self.draw_text('2. Continue', 0.3, self.settings['colors']['black'])
        self.draw_text('3. Leaderboard', 0.4, self.settings['colors']['black'])
        self.draw_text('4. Settings', 0.5, self.settings['colors']['black'])
        self.draw_text('5. Tutorial', 0.6, self.settings['colors']['black'])
        self.draw_text('6. Quit', 0.7, self.settings['colors']['black'])

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.set_current_screen('new_game')
            elif event.key == pygame.K_2:
                if savedgame:
                    self.set_current_screen(GameScreenManager(savedgame['difficulty'], savedgame['player_name']))
            elif event.key == pygame.K_3:
                self.set_current_screen('leaderboard')
            elif event.key == pygame.K_4:
                self.set_current_screen('settings')
            elif event.key == pygame.K_5:
                self.set_current_screen('tutorial')
            elif event.key == pygame.K_6:
                self.save_and_quit()

class NewGameScreen(ScreenManager):
    def __init__(self, screen, font, settings, set_current_screen, popup_manager, sprites):
        super().__init__(screen, font, settings, set_current_screen)
        self.popup_manager = popup_manager
        self.showing_popup = False
        self.difficulty = None
        self.sprites = sprites

    def display(self):
        self.screen.fill(self.settings['colors']['white'])
        if self.showing_popup:
            self.popup_manager.draw_popup("Warning: Adventure mode is difficult!", ["START", "BACK"])
        else:
            self.draw_text('Select Difficulty', 0.1, self.settings['colors']['black'])
            self.draw_text('1. Easy', 0.2, self.settings['colors']['black'])
            self.draw_text('2. Intermediate', 0.3, self.settings['colors']['black'])
            self.draw_text('3. Hard', 0.4, self.settings['colors']['black'])
            self.draw_text('4. Adventure', 0.5, self.settings['colors']['black'])
            self.draw_text('5. Back', 0.6, self.settings['colors']['black'])

    def handle_event(self, event):
        if self.showing_popup:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.start_game(self.difficulty)
                elif event.key == pygame.K_2:
                    self.showing_popup = False
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.start_game('easy')
                elif event.key == pygame.K_2:
                    self.start_game('intermediate')
                elif event.key == pygame.K_3:
                    self.start_game('hard')
                elif event.key == pygame.K_4:
                    self.difficulty = 'adventure'
                    self.show_adventure_warning()
                elif event.key == pygame.K_5:
                    self.set_current_screen('title')

    def start_game(self, difficulty):
        self.set_current_screen(GameScreenManager(difficulty, "Player"))

    def show_adventure_warning(self):
        self.showing_popup = True


class SettingsScreen(ScreenManager):
    def __init__(self, screen, font, settings, set_current_screen, popup_manager):
        super().__init__(screen, font, settings, set_current_screen)
        self.popup_manager = popup_manager
        self.volume = 0.5  # Default volume
        self.showing_popup = False
        self.popup_message = ""
        self.popup_options = []

    def display(self):
        self.screen.fill(self.settings['colors']['white'])
        if self.showing_popup:
            self.popup_manager.draw_popup(self.popup_message, ["CONTINUE", "BACK"])
        else:
            self.draw_text('Settings', 0.1, self.settings['colors']['black'])
            self.draw_text('1. Change Volume', 0.2, self.settings['colors']['black'])
            self.draw_volume_slider(0.3)
            self.draw_text('2. Reset Leaderboard', 0.4, self.settings['colors']['black'])
            self.draw_text('3. Erase Match Record', 0.5, self.settings['colors']['black'])
            self.draw_text('4. Quit', 0.6, self.settings['colors']['black'])
            self.draw_text('5. Back', 0.7, self.settings['colors']['black'])

            # Display match record
            self.draw_text('Match Record:', 0.75, self.settings['colors']['black'])
            for i, (difficulty, record) in enumerate(matchrecord.items()):
                self.draw_text(
                    f"{difficulty.capitalize()}: Played: {record['games_played']}, Won: {record['games_won']}, Lost: {record['games_lost']}, Win rate: {record['win_rate']}%",
                    0.8 + 0.05 * i,
                    self.settings['colors']['black']
                )

    def draw_volume_slider(self, y_ratio):
        screen_width, screen_height = self.screen.get_size()
        y = int(screen_height * y_ratio)
        slider_width = int(screen_width * 0.6)
        slider_height = 20
        slider_x = (screen_width - slider_width) // 2
        slider_y = y - slider_height // 2

        # Draw the slider background
        pygame.draw.rect(self.screen, self.settings['colors']['gray'], (slider_x, slider_y, slider_width, slider_height))
        # Draw the slider foreground
        volume_width = int(slider_width * self.volume)
        pygame.draw.rect(self.screen, self.settings['colors']['black'], (slider_x, slider_y, volume_width, slider_height))

    def handle_event(self, event):
        if self.showing_popup:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.perform_popup_action()
                elif event.key == pygame.K_2:
                    self.showing_popup = False
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.update_volume(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_2:
                    self.show_reset_leaderboard_warning()
                elif event.key == pygame.K_3:
                    self.show_erase_match_record_warning()
                elif event.key == pygame.K_4:
                    self.show_quit_warning()
                elif event.key == pygame.K_5:
                    self.set_current_screen('title')

    def update_volume(self, pos):
        screen_width, screen_height = self.screen.get_size()
        slider_width = int(screen_width * 0.6)
        slider_x = (screen_width - slider_width) // 2
        slider_y = int(screen_height * 0.3) - 10

        if slider_x <= pos[0] <= slider_x + slider_width and slider_y <= pos[1] <= slider_y + 20:
            self.volume = (pos[0] - slider_x) / slider_width
            pygame.mixer.music.set_volume(self.volume)  # Update the game volume

    def show_reset_leaderboard_warning(self):
        self.popup_message = "Warning: Resetting leaderboard!"
        self.showing_popup = True

    def show_erase_match_record_warning(self):
        self.popup_message = "Warning: Erasing match record!"
        self.showing_popup = True

    def show_quit_warning(self):
        self.popup_message = "Warning: Game state will be saved automatically!"
        self.showing_popup = True

    def perform_popup_action(self):
        if "Resetting leaderboard!" in self.popup_message:
            self.reset_leaderboard()
        elif "Erasing match record!" in self.popup_message:
            self.erase_match_record()
        elif "Game state will be saved automatically!" in self.popup_message:
            self.save_and_quit()
        self.showing_popup = False

    def reset_leaderboard(self):
        save_json("leaderboard", {})
        print("Leaderboard reset")

    def erase_match_record(self):
        save_json("matchrecord", {})
        print("Match record erased")

class LeaderboardScreen(ScreenManager):
    def __init__(self, screen, font, settings, leaderboard, set_current_screen):
        super().__init__(screen, font, settings, set_current_screen)
        self.leaderboard = leaderboard if leaderboard else {}

    def display(self):
        self.screen.fill(self.settings['colors']['white'])
        self.draw_text('Leaderboard', 0.1, self.settings['colors']['black'])
        difficulties = ['Easy', 'Intermediate', 'Hard', 'Adventure']
        for i, difficulty in enumerate(difficulties):
            self.draw_text(f'{difficulty}:', 0.2 + i * 0.15, self.settings['colors']['black'])
            scores = self.leaderboard.get(difficulty.lower(), [])
            for j in range(5):
                if j < len(scores):
                    score = scores[j]
                    self.draw_text(f'{j + 1}. {score["name"]} - {score["time"]}s', 0.25 + i * 0.15 + j * 0.05, self.settings['colors']['black'])
                else:
                    self.draw_text(f'{j + 1}. ---', 0.25 + i * 0.15 + j * 0.05, self.settings['colors']['black'])
        self.draw_text('4. Back', 0.85, self.settings['colors']['black'])

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_4:
                self.set_current_screen('title')

class TutorialScreen(ScreenManager):
    def __init__(self, screen, font, settings, set_current_screen):
        super().__init__(screen, font, settings, set_current_screen)
        self.page = 0
        self.pages = [
            "Welcome to Minesweeper! Click on tiles to uncover them.",
            "Flag mines to avoid them. Numbers indicate adjacent mines.",
            "Use logic to avoid mines and uncover all safe tiles! Press ENTER to start a New Game."
        ]
        self.gif_images = [pygame.image.load('sprites/tutorial.gif'), pygame.image.load('sprites/tutorial2.gif'), pygame.image.load('sprites/tutorial3.gif')]

    def display(self):
        self.screen.fill(self.settings['colors']['white'])
        self.screen.blit(self.gif_images[self.page], (self.screen.get_width() // 2 - self.gif_images[self.page].get_width() // 2, 50))
        self.draw_text(self.pages[self.page], 0.8, self.settings['colors']['black'])
        self.draw_text('Use LEFT and RIGHT arrows to navigate', 0.9, self.settings['colors']['black'])
        self.draw_text('4. Back', 0.95, self.settings['colors']['black'])

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.page = (self.page + 1) % len(self.pages)
            elif event.key == pygame.K_LEFT:
                self.page = (self.page - 1) % len(self.pages)
            elif event.key == pygame.K_RETURN and self.page == len(self.pages) - 1:
                self.set_current_screen('new_game')
            elif event.key == pygame.K_4:
                self.set_current_screen('title')

class MessagePopup:
    def __init__(self, screen, font, settings):
        self.screen = screen
        self.font = font
        self.settings = settings

    def draw_popup(self, message, options):
        screen_width, screen_height = self.screen.get_size()
        popup_rect = pygame.Rect(screen_width // 4, screen_height // 4, screen_width // 2, screen_height // 2)
        pygame.draw.rect(self.screen, self.settings['colors']['gray'], popup_rect)
        pygame.draw.rect(self.screen, self.settings['colors']['black'], popup_rect, 2)
        self.draw_text(message, popup_rect.centery - 50)

        for i, option in enumerate(options):
            self.draw_text(f'{i + 1}. {option}', popup_rect.centery + 30 + i * 40)

    def draw_text(self, text, y, color=(0, 0, 0)):
        screen_width, screen_height = self.screen.get_size()
        textobj = self.font.render(text, True, color)
        textrect = textobj.get_rect(center=(screen_width // 2, y))
        self.screen.blit(textobj, textrect)