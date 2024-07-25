# Description: Module to define game functions and classes.
# Chief contributor: JH Kim,DY Kim, SS Lee

import pygame
import random
from io_settings import load_json,save_json

# types list
# "X" -> mine
# "C{num}" -> clue (number)
# "/" -> empty

# dug list
# 0 -> dug
# 1 -> undug
# 2 -> flag
# 3 -> unsure_flag

# Tile class - simple class defining tile properties
class Tile:
    def __init__(self,x,y,type,revealed=False,flagged=False,unsure_flag=False):
        '''Function to initialize the tile with x,y coordinates,type,and revealed,flagged,unsure_flag properties.'''
        self.x,self.y = x,y # x,y coordinates
        self.type = type # type of tile -mine,clue,empty,flag
        self.revealed = revealed # revealed or not
        self.flagged = flagged # flagged or not
        self.unsure_flag = unsure_flag # unsure flag or not
    
    def __repr__(self):
        return self.type

# Board class - class defining board properties and methods
class Board:
    def __init__(self,rows,cols,mines):
        '''Function to initialize the board with rows,columns,and mines.'''
        self.rows = rows # number of rows
        self.cols = cols # number of columns
        self.mines = mines # number of mines
        self.flags = 0 # number of flags
    
    def new_game(self):
        self.game_over = False # game over or not
        self.board_list = [[Tile(col,row,"/") for row in range(self.rows)] for col in range(self.cols)]  # 2D list of tiles
        self.dug = [[1 for _ in range(self.rows)] for _ in range(self.cols)] # 2D mask list to check if tile is dug,undug,flagged,or unsure.
        self.valid_clicks = 0 # Valid clicks (left clicks resulting in non-mine tiles)
        self.guess_mines = self.mines - self.flags # number of guessed mines - calculated as mines - flags
        self.place_mines(self.mines) # place mines
        self.place_clues() # place clues
    
    # Methods to place mines and clues    
    def place_mines(self,mines):
        '''Function to initially place mines randomly on the board.'''
        for _ in range(mines):
            while True:
                x = random.randint(0,self.rows-1)
                y = random.randint(0,self.cols-1)

                if self.board_list[x][y].type == "/" and self.dug[x][y]: # if the tile is empty and not dug
                    self.board_list[x][y].type = "X"
                    break
    
    def is_inside(self,x,y):
        '''Function to check if the given coordinates are inside the board.'''
        return 0 <= x < self.rows and 0 <= y < self.cols
    
    def check_neighbors(self,x,y):
        '''Function to check the number of mines around the given tile. Used to place clues.'''
        total_mines = 0
        for i in range(-1,2):
            for j in range(-1,2): # check 8 neighbors
                if i == 0 and j == 0: # skip the tile itself
                    continue
                elif self.is_inside(x+i,y+j) and self.board_list[x+i][y+j].type == "X": # if the neighbor is a mine
                    total_mines+=1
        return total_mines
    
    def place_clues(self):
        '''Function to place clues on the board based on the number of mines around the tile.'''
        for x in range(self.rows):
            for y in range(self.cols):
                if self.board_list[x][y].type != "X": # if the tile is not a mine
                    total_mines = self.check_neighbors(x,y)
                    if total_mines > 0: # if there are mines around the tile
                        self.board_list[x][y].type = f"C{total_mines}"

    # Methods to dig and flag tiles
    def dig(self,x,y):
        '''Function to dig the tile at the given coordinates. Recursively digs if empty,nonclue tiles are dug.'''
        if not self.is_inside(x,y) or self.board_list[x][y].revealed: # if the coordinates are outside the board or already revealed
            return

        # Add the tile to the list of dug tiles
        self.board_list[x][y].revealed = True
        self.board_list[x][y].flagged = False
        self.board_list[x][y].unsure_flag = False
        self.dug[x][y] = 0
        
        if self.board_list[x][y].type == "/": # if the tile is empty
            for i in range(-1,2):
                for j in range(-1,2): # check 8 neighbors
                    if not (i == 0 and j == 0): # skip the tile itself
                        self.dig(x+i,y+j) # recursively dig the neighbors

        elif self.board_list[x][y].type.startswith("C"): # if the tile is a clue
            return

    def left_click(self,x,y):
        '''Function to handle left click on the tile at the given coordinates.'''
        if not self.is_inside(x,y): # if the coordinates are outside the board
            return "No Action"
        if self.board_list[x][y].type == "X": # if the tile is a mine
            self.board_list[x][y].revealed = True
            self.game_over = True
            return "Game Over"
        else: # if the tile is not a mine - run dig()
            self.dig(x,y)
            self.valid_clicks+=1
            return "Continue"

    def right_click(self,x,y):
        '''Function to handle right click on the tile at the given coordinates.'''
        if self.dug[x][y] == 0: # if the tile is already dug
            return "No Action"
        elif self.dug[x][y] == 1: # if the tile is not dug
            self.board_list[x][y].flagged = True
            self.board_list[x][y].unsure_flag = False
            self.flags+=1
            self.guess_mines = self.mines - self.flags
            self.dug[x][y] = 2
        elif self.dug[x][y] == 2: # if the tile is flagged
            self.board_list[x][y].flagged = False
            self.board_list[x][y].unsure_flag = True
            self.flags -= 1
            self.guess_mines = self.mines - self.flags
            self.dug[x][y] = 3
        elif self.dug[x][y] == 3: # if the tile is unsure_flag
            self.board_list[x][y].flagged = False
            self.board_list[x][y].unsure_flag = False
            self.dug[x][y] = 1
        
    def middle_click(self,x,y):
        '''Function to handle middle click on the tile at the given coordinates.'''
        if self.dug[x][y] == 0 and self.board_list[x][y].type.startswith("C"): # if the tile is dug and is a clue
            total_flags = 0 
            for i in range(-1,2):
                for j in range(-1,2): # count the number of flags around the tile
                    if i == 0 and j == 0: # skip the tile itself
                        continue
                    if self.is_inside(x,y) and self.is_inside(x+i,y+j) and self.dug[x+i][y+j] == 2: # if the neighbor is flagged
                        total_flags+=1
            if total_flags == int(self.board_list[x][y].type[1:]): # if the number of flags around the tile is equal to the clue number
                for i in range(-1,2):
                    for j in range(-1,2):
                        if i == 0 and j == 0: # skip the tile itself
                            continue
                        if self.is_inside(x,y): # if the coordinates are inside the board
                            valid_clicks = self.valid_clicks # temporary variable to hold valid_clicks
                            self.left_click(x+i,y+j) # dig the neighbors
                            self.valid_clicks = valid_clicks+1 # using mid_click only counts as one valid_click!
        
    # Methods to reset the board
    def set_mine(self,cnt_covered,elapsed_time,mode = "ratio"):
        '''Function to set the number of mines depending on the mode'''
        # Implement ML if possible
        if mode == "ml":
            pass
        elif mode == "adventure":
            adventure_mines = self.mines - (elapsed_time-40) // 2
            return self.mines - adventure_mines
        elif mode == "ratio":
            ratio = cnt_covered / (self.rows * self.cols)
            return int(ratio * self.mines)
        else:
            return self.mines

    def reset_board(self,elapsed_time,mode = "ratio"):
        '''Function to reset the board for mine and clue placement'''
        self.board_list = [[Tile(col,row,"/") for row in range(self.rows)] for col in range(self.cols)]
        self.valid_clicks = 0
        self.flags = 0
        cnt_covered = sum([sum([not tile.revealed for tile in row]) for row in self.board_list])
        self.mines = self.set_mine(cnt_covered,elapsed_time,mode)
        self.place_mines(self.mines)
        self.place_clues()
        self.guess_mines = self.mines - self.flags
    
    def remove_mine(self):
        covered_mines = [(x, y) for x in range(self.rows) for y in range(self.cols) if self.board_list[x][y].type == "X" and not self.board_list[x][y].revealed]
        if covered_mines:
            x, y = random.choice(covered_mines)
            self.board_list[x][y].type = "/"
            self.mines -= 1
            if self.dug[x][y] == 2:
                self.flags -= 1
            self.guess_mines = self.mines - self.flags
            self.place_clues()
    
    # Methods to check win and lose conditions
    def check_win(self):
        '''Function to check if the player has won the game.'''
        for row in self.board_list:
            for tile in row:
                if not tile.revealed and tile.type != "X": # if there are still unrevealed non-mine tiles
                    return False
                elif tile.revealed and tile.type == "X":
                    return False
        return True

    
class GameContainer:
    def __init__(self,difficulty):
        self.difficulty = difficulty
        self.settings = load_json("settings")
        self.savedgame = load_json("savedgame")
        self.leaderboard = load_json("leaderboard")
        self.matchrecord = load_json("matchrecord")
    
    def start_game(self, start_time):
        self.start_time = start_time
        self.game_over = False
        self.win = False
        self.board = Board(*self.settings['game_settings'][self.difficulty])
        self.board.new_game()

    def update_match_record(self,result):
        difficulty_record = self.matchrecord.get(self.difficulty)
        if not difficulty_record:
            difficulty_record = {
                'games_played': 0,
                'games_won': 0,
                'games_lost': 0,
                'win_rate': 0
            }
        difficulty_record['games_played']+=1
        if result:
            difficulty_record['games_won']+=1
        else:
            difficulty_record['games_lost']+=1

        if difficulty_record['games_played'] > 0:
            difficulty_record['win_rate'] = round(
                (difficulty_record['games_won'] / difficulty_record['games_played']) * 100,2
            )

        self.matchrecord[self.difficulty] = difficulty_record
        save_json("matchrecord",self.matchrecord)

    def add_to_leaderboard(self,player_name,elapsed_time):
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        new_entry = {
            "name": player_name,
            "time": elapsed_time
        }
        if self.difficulty in self.leaderboard:
            self.leaderboard[self.difficulty].append(new_entry)
            self.leaderboard[self.difficulty] = sorted(self.leaderboard[self.difficulty],key=lambda x: x["time"])[:5]
        else:
            self.leaderboard[self.difficulty] = [new_entry]
        save_json("self.leaderboard",self.leaderboard)

    def save_game_state(self):
        game_state = {
            self.difficulty: {
                'board': [[tile.type for tile in row] for row in self.board.board_list],
                'covered': [[not tile.revealed for tile in row] for row in self.board.board_list],
                'flags': self.board.flags,
                'game_over': self.game_over,
                'start_time': self.start_time
            }
        }
        save_json("savedgame",game_state)
    
    def delete_save_game(self):
        if self.difficulty in self.savedgame:
            self.savedgame[self.difficulty] = {}
        save_json("savedgame",self.savedgame)
    
    def load_game_state(self, savedgame):
        if self.difficulty in savedgame:
            game_state = savedgame[self.difficulty]
            self.board.board_list = [[Tile(col,row,game_state['board'][col][row],not game_state['covered'][col][row]) for row in range(self.board.rows)] for col in range(self.board.cols)]
            self.board.flags = game_state['flags']
            self.game_over = game_state['game_over']
            self.start_time = game_state['start_time']
            self.board.valid_clicks = sum([sum([not tile.revealed for tile in row]) for row in self.board.board_list])
            self.board.guess_mines = self.board.mines - self.board.flags
            return True
        return False

    def adventure_mode(self):
        # In adventure mode, the time ticks down from 300 seconds. If the time runs out, the player loses. After 40 seconds, the number of mines decreases by 1 every 2 seconds. Every 30 seconds, the position of mines changes.
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        if elapsed_time >= 300:
            self.game_over = True
            self.win = False
            return
        elif elapsed_time % 60 == 0 and elapsed_time != self.last_reset:
            self.board.reset_board(elapsed_time, "adventure")
            self.last_reset = elapsed_time
        elif elapsed_time >= 40 and elapsed_time % 2 == 0 and elapsed_time != self.last_mine_removal:
            self.last_mine_removal = elapsed_time
            self.board.remove_mine()
        if self.board.check_win():
            self.game_over = True
            self.win = True
            return