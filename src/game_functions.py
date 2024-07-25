import pygame
import random
from io_settings import load_json, save_json

# types list
# "X" -> mine
# "C{num}" -> clue (number)
# "/" -> empty

# dug list
# 0 -> dug
# 1 -> undug
# 2 -> flag
# 3 -> unsure_flag

class Tile:
    def __init__(self, x, y, type, revealed=False, flagged=False, unsure_flag=False):
        self.x, self.y = x, y
        self.type = type
        self.revealed = revealed
        self.flagged = flagged
        self.unsure_flag = unsure_flag
    
    def __repr__(self):
        return self.type

class Board:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.flags = 0
    
    def new_game(self):
        self.game_over = False
        self.board_list = [[Tile(col, row, "/") for row in range(self.rows)] for col in range(self.cols)]
        self.dug = [[1 for _ in range(self.rows)] for _ in range(self.cols)]
        self.valid_clicks = 0
        self.guess_mines = self.mines - self.flags
        self.place_mines(self.mines)
        self.place_clues()
    
    def place_mines(self, mines):
        for _ in range(mines):
            while True:
                x = random.randint(0, self.rows - 1)
                y = random.randint(0, self.cols - 1)

                if self.board_list[x][y].type == "/" and self.dug[x][y]:
                    self.board_list[x][y].type = "X"
                    break
    
    def is_inside(self, x, y):
        return 0 <= x < self.rows and 0 <= y < self.cols
    
    def check_neighbors(self, x, y):
        total_mines = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                elif self.is_inside(x + i, y + j) and self.board_list[x + i][y + j].type == "X":
                    total_mines += 1
        return total_mines
    
    def place_clues(self):
        for x in range(self.rows):
            for y in range(self.cols):
                if self.board_list[x][y].type != "X":
                    total_mines = self.check_neighbors(x, y)
                    if total_mines > 0:
                        self.board_list[x][y].type = f"C{total_mines}"
    
    def dig(self, x, y):
        if not self.is_inside(x, y) or self.board_list[x][y].revealed:
            return

        self.board_list[x][y].revealed = True
        self.board_list[x][y].flagged = False
        self.board_list[x][y].unsure_flag = False
        self.dug[x][y] = 0
        
        if self.board_list[x][y].type == "/":
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if not (i == 0 and j == 0):
                        self.dig(x + i, y + j)
        elif self.board_list[x][y].type.startswith("C"):
            return
    
    def left_click(self, x, y):
        if not self.is_inside(x, y):
            return "No Action"
        if self.board_list[x][y].type == "X":
            self.board_list[x][y].revealed = True
            self.game_over = True
            return "Game Over"
        else:
            self.dig(x, y)
            self.valid_clicks += 1
            return "Continue"
    
    def right_click(self, x, y):
        if self.dug[x][y] == 0:
            return "No Action"
        elif self.dug[x][y] == 1:
            self.board_list[x][y].flagged = True
            self.board_list[x][y].unsure_flag = False
            self.flags += 1
            self.guess_mines = self.mines - self.flags
            self.dug[x][y] = 2
        elif self.dug[x][y] == 2:
            self.board_list[x][y].flagged = False
            self.board_list[x][y].unsure_flag = True
            self.flags -= 1
            self.guess_mines = self.mines - self.flags
            self.dug[x][y] = 3
        elif self.dug[x][y] == 3:
            self.board_list[x][y].flagged = False
            self.board_list[x][y].unsure_flag = False
            self.dug[x][y] = 1
    
    def middle_click(self, x, y):
        if self.dug[x][y] == 0 and self.board_list[x][y].type.startswith("C"):
            total_flags = 0 
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0:
                        continue
                    if self.is_inside(x + i, y + j) and self.dug[x + i][y + j] == 2:
                        total_flags += 1
            if total_flags == int(self.board_list[x][y].type[1:]):
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if i == 0 and j == 0:
                            continue
                        if self.is_inside(x + i, y + j) and not self.board_list[x + i][y + j].flagged:
                            valid_clicks = self.valid_clicks
                            self.left_click(x + i, y + j)
                            self.valid_clicks = valid_clicks + 1

    def set_mine(self, cnt_covered, elapsed_time, mode="ratio"):
        if mode == "ml":
            pass
        elif mode == "adventure":
            adventure_mines = self.mines - (elapsed_time - 40) // 2
            return self.mines - adventure_mines
        elif mode == "ratio":
            ratio = cnt_covered / (self.rows * self.cols)
            return int(ratio * self.mines)
        else:
            return self.mines

    def reset_board(self, elapsed_time, mode="ratio"):
        # Retain the state of uncovered tiles
        for row in self.board_list:
            for tile in row:
                if not tile.revealed:
                    tile.type = "/"

        cnt_covered = sum([sum([not tile.revealed for tile in row]) for row in self.board_list])
        self.mines = self.set_mine(cnt_covered, elapsed_time, mode)
        self.place_mines(self.mines)
        self.place_clues()
        self.valid_clicks = 0

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
    
    def check_win(self):
        for row in self.board_list:
            for tile in row:
                if not tile.revealed and tile.type != "X":
                    return False
                elif tile.revealed and tile.type == "X":
                    return False
        return True

class GameContainer:
    def __init__(self, difficulty):
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

    def update_match_record(self, result):
        difficulty_record = self.matchrecord.get(self.difficulty)
        if not difficulty_record:
            difficulty_record = {
                'games_played': 0,
                'games_won': 0,
                'games_lost': 0,
                'win_rate': 0
            }
        for val in difficulty_record.values():
            if type(val) != int and val !="---":
                val == int(val)
        difficulty_record['games_played'] += 1
        if result:
            difficulty_record['games_won'] += 1
        else:
            difficulty_record['games_lost'] += 1

        if difficulty_record['games_played'] > 0:
            difficulty_record['win_rate'] = round(
                (difficulty_record['games_won'] / difficulty_record['games_played']) * 100, 2
            )

        self.matchrecord[self.difficulty] = difficulty_record
        save_json("matchrecord", self.matchrecord)

    def add_to_leaderboard(self, player_name, elapsed_time):
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        new_entry = {
            "name": player_name,
            "time": elapsed_time
        }
        if self.difficulty in self.leaderboard:
            self.leaderboard[self.difficulty].append(new_entry)
            self.leaderboard[self.difficulty] = sorted(self.leaderboard[self.difficulty], key=lambda x: x["time"])[:5]
        else:
            self.leaderboard[self.difficulty] = [new_entry]
        save_json("leaderboard", self.leaderboard)

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
        save_json("savedgame", game_state)
    
    def delete_save_game(self):
        if self.difficulty in self.savedgame:
            self.savedgame[self.difficulty] = {}
        save_json("savedgame", self.savedgame)
    
    def load_game_state(self, savedgame):
        if self.difficulty in savedgame:
            game_state = savedgame[self.difficulty]
            self.board.board_list = [[Tile(col, row, game_state['board'][col][row], not game_state['covered'][col][row]) for row in range(self.board.rows)] for col in range(self.board.cols)]
            self.board.flags = game_state['flags']
            self.game_over = game_state['game_over']
            self.start_time = game_state['start_time']
            self.board.valid_clicks = sum([sum([not tile.revealed for tile in row]) for row in self.board.board_list])
            self.board.guess_mines = self.board.mines - self.board.flags
            return True
        return False

    def adventure_mode(self):
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