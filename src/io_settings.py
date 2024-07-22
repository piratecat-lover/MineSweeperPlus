import json
import os
import pygame

# (Private) Hidden directory to store settings and data
_HIDDEN_DIR = os.path.join("./", ".minesweeper_data")

# Ensure hidden directory exists
if not os.path.exists(_HIDDEN_DIR):
    os.makedirs(_HIDDEN_DIR)

# Functions to load and save gamefiles to json
def load_json(file_name):
    '''Load JSON data from a file.'''
    if not os.path.exists(os.path.join(_HIDDEN_DIR, f"{file_name}.json")):
        return {}
    with open(os.path.join(_HIDDEN_DIR, f"{file_name}.json"), 'r') as file:
        data = json.load(file)
    return data

def save_json(file_name, data):
    '''Save JSON data to a file.'''
    with open(os.path.join(_HIDDEN_DIR, f"{file_name}.json"), 'w') as file:
        json.dump(data, file, indent=4)

# (Public) Variables storing game settings and data
settings = load_json("settings")
leaderboard = load_json("leaderboard")
matchrecord = load_json("matchrecord")
savedgame = load_json("savedgame")

# Function to load sprites
def load_sprites(settings):
    sprites = {}
    for key, path in settings['sprites'].items():
        if isinstance(path, list):
            sprites[key] = [pygame.transform.scale(pygame.image.load(p), (32,32)) for p in path]
        else:
            sprites[key] = pygame.transform.scale(pygame.image.load(path), (32,32))
    return sprites