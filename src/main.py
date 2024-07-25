import pygame
import sys
from screen_manager import *
from game_manager import DisplayGameContainer
from io_settings import load_json

def main():
    pygame.init()
    settings = load_json("settings")
    screen = pygame.display.set_mode((settings['screen_width'], settings['screen_height']))
    font = pygame.font.Font(None, settings['font_size'])
    popup_manager = MessagePopup(screen, font, settings)
    current_screen = None
    
    def set_current_screen(screen_name):
        nonlocal current_screen
        if screen_name == 'title':
            current_screen = TitleScreen(screen, font, settings, set_current_screen)
        elif screen_name == 'new_game':
            current_screen = NewGameScreen(screen, font, settings, set_current_screen, popup_manager)
        elif screen_name == 'continue_game':
            current_screen = ContinueGameScreen(screen, font, settings, set_current_screen, popup_manager)
        elif screen_name == 'leaderboard':
            current_screen = LeaderboardScreen(screen, font, settings, set_current_screen)
        elif screen_name == 'settings':
            current_screen = SettingsScreen(screen, font, settings, set_current_screen, popup_manager)
        elif screen_name == 'tutorial':
            current_screen = TutorialScreen(screen, font, settings, set_current_screen)
        elif isinstance(screen_name, DisplayGameContainer):
            current_screen = screen_name
        else:
            current_screen = screen_name
    
    set_current_screen('title')
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            current_screen.handle_event(event)
        
        current_screen.display()
        pygame.display.flip()

if __name__ == "__main__":
    main()
