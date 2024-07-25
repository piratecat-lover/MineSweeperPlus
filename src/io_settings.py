# Description: Module to save/load settings and data to/from json files.
# Chief contributor: SS Lee

# Import packages
import json
import os

# (Private) Hidden directory to store settings and data
_HIDDEN_DIR = os.path.join("./", ".minesweeper_data")

# (Public) Function to create hidden settings directory if it does not exist
def make_folder():
    '''Create a hidden folder to store settings and data.'''
    if not os.path.exists(_HIDDEN_DIR):
        os.makedirs(_HIDDEN_DIR)

# (Public) Function to load game data from json file
def load_json(file_name):
    if file_name.startswith("self."):
        file_name = file_name[5:]
    '''Load JSON data from a file.'''
    if not os.path.exists(os.path.join(_HIDDEN_DIR, f"{file_name}.json")):
        return {}
    with open(os.path.join(_HIDDEN_DIR, f"{file_name}.json"), 'r') as file:
        data = json.load(file)
    return data

# (Public) Function to save game data to json file
def save_json(file_name, data):
    '''Save JSON data to a file.'''
    if file_name.startswith("self."):
        file_name = file_name[5:]
    with open(os.path.join(_HIDDEN_DIR, f"{file_name}.json"), 'w') as file:
        json.dump(data, file, indent=4)