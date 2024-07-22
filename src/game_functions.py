# File to store gameplay functions without graphics
import pygame
import random
from io_settings import leaderboard, matchrecord, savedgame, save_json, load_json


# types list
# "X" -> mine
# "C{num}" -> clue (number)
# "/" -> empty
# "F" -> flag

# Tile class
class Tile:
    def __init__(self, x, y, type, revealed=False, flagged=False):
        self.x, self.y = x, y
        self.type = type
        self.revealed = revealed
        self.flagged = flagged
    
    def __repr__(self):
        return self.type

# Board class
class Board:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.guess_mines = mines
        self.flags = 0
        self.board_list = [[Tile(col, row, "/") for row in range(rows)] for col in range(cols)]
        self.dug = [[0 for _ in range(rows)] for _ in range(cols)]
    
    def place_mines(self):
        for _ in range(self.mines):
            while True:
                x = random.randint(0, self.rows-1)
                y = random.randint(0, self.cols-1)

                if self.board_list[x][y].type == "/" and self.dug[x][y] == 0:
                    self.board_list[x][y].type = "X"
                    break
    
    def is_inside(self, x, y):
        return 0 <= x < self.rows and 0 <= y < self.cols
    
    def check_neighbours(self, x, y):
        total_mines = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                elif self.is_inside(x+i, y+j) and self.board_list[x+i][y+j].type == "X":
                    total_mines+=1
        return total_mines
    
    def place_clues(self):
        for x in range(self.rows):
            for y in range(self.cols):
                if self.board_list[x][y].type != "X":
                    total_mines = self.check_neighbours(x, y)
                    if total_mines > 0:
                        self.board_list[x][y].type = f"C{total_mines}"
    
    def reset_board(self):
        self.board_list = [[Tile(col, row, "/") for row in range(self.rows)] for col in range(self.cols)]
        self.place_mines()
        self.place_clues()
        
    
    def left_click(self, x, y):
        if self.board_list[x][y].type == "X":
            return "Game Over"
        else:
            self.board_list[x][y].revealed = True
            self.dug[x][y] = 1
            return "Continue"
    
    def right_click(self, x, y):
        if self.board_list[x][y].type == ".":
            self.board_list[x][y].type = "F"
            self.guess_mines-=1
            self.flags+=1
        elif self.board_list[x][y].type == "F":
            self.board_list[x][y].type = "."
            self.guess_mines+=1
            self.flags-=1
        return "Continue"
    
    def dig(self, x, y):
        if self.board_list[x][y].type == "X":
            self.board_list[x][y].revealed = True
            return False
        elif self.board_list[x][y].type.startswith("C"):
            self.board_list[x][y].revealed = True
            return True
        else:
            self.board_list[x][y].revealed = True
            self.dug[x][y] = 1
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0:
                        continue
                    if self.is_inside(x+i, y+j) and not self.board_list[x+i][y+j].revealed:
                        self.dig(x+i, y+j)
            return True

class GameContainer:
    def __init__(self, difficulty, player_name="Player"):
        self.difficulty = difficulty
        self.player_name = player_name
        self.start_time = 0
        self.flags = 0
        self.game_over = False
        self.win = False

    def update_match_record(self, result):
        difficulty_record = matchrecord[self.difficulty]
        difficulty_record['games_played'] += 1
        if result == 'won':
            difficulty_record['games_won'] += 1
        else:
            difficulty_record['games_lost'] += 1

        if difficulty_record['games_played'] > 0:
            difficulty_record['win_rate'] = round(
                (difficulty_record['games_won'] / difficulty_record['games_played']) * 100, 2
            )

        matchrecord[self.difficulty] = difficulty_record
        save_json("matchrecord", matchrecord)

    def add_to_leaderboard(self):
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        new_entry = {
            "name": self.player_name,
            "time": elapsed_time
        }
        if self.difficulty in leaderboard:
            leaderboard[self.difficulty].append(new_entry)
            leaderboard[self.difficulty] = sorted(leaderboard[self.difficulty], key=lambda x: x["time"])[:5]
        else:
            leaderboard[self.difficulty] = [new_entry]
        save_json("leaderboard", leaderboard)

    def save_game_state(self, board):
        game_state = {
            self.difficulty: {
                'board': [[tile.type for tile in row] for row in board.board_list],
                'covered': [[not tile.revealed for tile in row] for row in board.board_list],
                'flags': self.flags,
                'game_over': self.game_over,
                'win': self.win,
                'start_time': self.start_time,
            }
        }
        save_json("savedgame", game_state)
    
    def delete_save_game(self):
        if self.difficulty in savedgame:
            savedgame[self.difficulty] = {}
        save_json("savedgame", savedgame)

