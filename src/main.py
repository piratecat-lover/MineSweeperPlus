import pygame
from screen_manager import *
from game_manager import GameScreenManager
from io_settings import load_sprites, settings, leaderboard

def set_current_screen(screen_name):
    global current_screen
    current_screen = screen_name

def main():
    # Initialize Pygame
    pygame.init()

    # Constants
    global FPS, TILESIZE, HEADERSIZE, WHITE
    FPS = settings.get('fps', 60)
    TILESIZE = 32
    HEADERSIZE = 60
    WHITE = tuple(settings['colors']['white'])

    # Initialize screen and other elements
    screen = pygame.display.set_mode((800, 450), pygame.RESIZABLE)
    pygame.display.set_caption("Minesweeper")
    clock = pygame.time.Clock()

    # Initialize font
    font = pygame.font.Font(None, settings['font_size'])

    # Load sprites
    sprites = load_sprites(settings)
    running = True

    title_screen = TitleScreen(screen, font, settings, set_current_screen)
    popup_manager = MessagePopup(screen, font, settings)
    new_game_screen = NewGameScreen(screen, font, settings, set_current_screen, popup_manager, sprites)
    settings_screen = SettingsScreen(screen, font, settings, set_current_screen, popup_manager)
    leaderboard_screen = LeaderboardScreen(screen, font, settings, leaderboard, set_current_screen)
    tutorial_screen = TutorialScreen(screen, font, settings, set_current_screen)

    global current_screen
    current_screen = 'title'

    screens = {
        'title': title_screen,
        'new_game': new_game_screen,
        'settings': settings_screen,
        'leaderboard': leaderboard_screen,
        'tutorial': tutorial_screen
    }

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if isinstance(current_screen, GameScreenManager):
                    current_screen.save_and_quit()
                elif current_screen in screens:
                    screens[current_screen].save_and_quit()
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif isinstance(current_screen, GameScreenManager):
                current_screen.handle_event(event)
            elif current_screen in screens:
                screens[current_screen].handle_event(event)

        screen.fill(WHITE)

        if isinstance(current_screen, GameScreenManager):
            current_screen.display()
        elif current_screen in screens:
            screens[current_screen].display()

        pygame.display.flip()
        clock.tick(FPS)

    if isinstance(current_screen, GameScreenManager):
        current_screen.save_and_quit()
    elif current_screen in screens:
        screens[current_screen].save_and_quit()

if __name__ == "__main__":
    main()