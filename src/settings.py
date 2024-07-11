# COLORS (r, g, b)
import pygame
import os

# COLORS (r, g, b)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
DARKGREEN = (0, 200, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BGCOLOUR = DARKGREY


# game settings
TILESIZE = 32
FPS = 60
TITLE = "Minesweeper with Moving Mines"
TITLE_WIDTH=800
TITLE_HEIGHT=450

# Default settings
ROWS, COLS, AMOUNT_MINES = 8, 8, 10
WIDTH = TILESIZE * COLS
HEIGHT = TILESIZE * ROWS + 50  # Extra space for banner

# Board options
BOARD_OPTIONS = {
    '8x8': (8, 8, 10),
    '16x16': (16, 16, 40),
    '30x16': (30, 16, 99)
}

# Leaderboard
LEADERBOARD = {
    '8x8': float('inf'),
    '16x16': float('inf'),
    '30x16': float('inf')
}

tile_numbers = []
for i in range(1, 9):
    tile_numbers.append(pygame.transform.scale(pygame.image.load(os.path.join("./sprites", f"Tile{i}.png")), (TILESIZE, TILESIZE)))

# Load images
tile_numbers = [pygame.transform.scale(pygame.image.load(os.path.join("./sprites", f"Tile{i}.png")), (TILESIZE, TILESIZE)) for i in range(1, 9)]
tile_empty = pygame.transform.scale(pygame.image.load(os.path.join("./sprites", "TileEmpty.png")), (TILESIZE, TILESIZE))
tile_exploded = pygame.transform.scale(pygame.image.load(os.path.join("./sprites", "TileExploded.png")), (TILESIZE, TILESIZE))
tile_flag = pygame.transform.scale(pygame.image.load(os.path.join("./sprites", "TileFlag.png")), (TILESIZE, TILESIZE))
tile_mine = pygame.transform.scale(pygame.image.load(os.path.join("./sprites", "TileMine.png")), (TILESIZE, TILESIZE))
tile_unknown = pygame.transform.scale(pygame.image.load(os.path.join("./sprites", "TileUnknown.png")), (TILESIZE, TILESIZE))
tile_not_mine = pygame.transform.scale(pygame.image.load(os.path.join("./sprites", "TileNotMine.png")), (TILESIZE, TILESIZE))

