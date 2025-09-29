from tkinter import *
from datetime import datetime
import json
import os


class PlayerTopScores:
    data = None  # format below
    #   [
    #       {
    #           "player_win": "X",
    #           "time_passed": 123
    #       },
    #       {
    #           "player_win": "O",
    #           "time_passed": 456
    #       }
    #   ]
    #

    # tkinter components
    labels = None

    def __init__(self, filename):
        self.labels = []
        if not os.path.isfile(filename):
            self.data = []
            return
        with open(filename) as f:
            self.data = json.load(f)

    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def add_new(self, player_win, time_passed):
        self.data.append({"player_win": player_win, "time_passed": time_passed})
        self.data.sort(key=lambda x: x["time_passed"])
        self.data = self.data[0:9]

    def render(self, window):
        # full rerender, no optimizations
        for label in self.labels:
            del label
        for idx, record in enumerate(self.data):
            time_passed = datetime.fromtimestamp(record["time_passed"]).strftime("%M:%S")
            label_time_passed = Label(window, font=('Comic Sans MS', 15), fg='green', text=time_passed)
            label_time_passed.place(x=380, y=30 + idx * 30)
            self.labels.append(label_time_passed)
            player_win = record["player_win"]
            label_player_win = Label(window, font=('Comic Sans MS', 15), fg='green', text=player_win)
            label_player_win.place(x=360, y=30 + idx * 30)
            self.labels.append(label_player_win)


class SingleGameData:
    WIN_LINES = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [6, 4, 2]]

    turn = None  # can be 'X' or 'O'
    field = None  # list of len 9 with None, 'X' or 'O'
    start_time = None

    def __init__(self):
        self.turn = 'X'
        self.field = [None] * 9
        self.start_time = datetime.now()  # TODO: count each player time separately

    def win_player_line(self):
        for win_line in self.WIN_LINES:
            fst_val = self.field[win_line[0]]
            if fst_val is None:
                continue
            for pos in win_line:
                if self.field[pos] != fst_val:
                    break
            else:
                return fst_val, win_line
        return None, None

    def make_move(self, pos, button):
        if self.field[pos] is not None:
            return False
        if self.win_player_line()[0] is not None:
            return False
        self.field[pos] = self.turn
        button.config(text=self.turn)
        if self.turn == 'X':
            self.turn = 'O'
        else:
            self.turn = 'X'
        return True


class Game:
    FIELD_BUTTON_WIDTH = 120

    current_game_data = None
    player_top_scores = None

    # tkinter components
    window = None
    field_buttons = None
    restart_button = None
    game_time_label = None
    player_top_scores_title_label = None

    def __init__(self):
        self.create_window_static_content()
        self.start_new_game()
        self.update_window()
        self.player_top_scores = PlayerTopScores('xo_top_scores.json')
        self.player_top_scores.render(self.window)
        self.window.mainloop()

    def create_binded_function(self, pos, button):
        return lambda _: self.on_field_click(pos, button)

    def create_window_static_content(self):
        self.window = Tk()
        self.window.geometry('450x400')
        self.window.title('крестики-нолики')

        self.field_buttons = []
        for i in range(3):
            for j in range(3):
                button = Button(bg="black", bd=5, font=("Comic Sans MS", 40, "bold"), fg='white')
                button.place(x=i * self.FIELD_BUTTON_WIDTH, y=j * self.FIELD_BUTTON_WIDTH,
                             width=self.FIELD_BUTTON_WIDTH, height=self.FIELD_BUTTON_WIDTH)
                button.bind("<Button-1>", self.create_binded_function(i * 3 + j, button))
                self.field_buttons.append(button)

        self.restart_button = Button(bg="green", bd=3, fg='white', text="restart")
        self.restart_button.place(x=0, y=360, width=160, height=40)
        self.restart_button.bind("<Button-1>", lambda _: self.start_new_game())

        self.player_top_scores_title_label = Label(self.window, font=('Comic Sans MS', 15), text='records')
        self.player_top_scores_title_label.place(x=360, y=0)

        self.game_time_label = Label(self.window, width=10, font=('Comic Sans MS', 15), text='00:00')
        self.game_time_label.place(x=160, y=360)

    def on_field_click(self, pos, button):
        move_made = self.current_game_data.make_move(pos, button)
        if move_made:
            self.end_game()

    def start_new_game(self):
        for button in self.field_buttons:
            button.config(text='', fg='white')
        self.current_game_data = SingleGameData()

    def end_game(self):
        win_player, win_line = self.current_game_data.win_player_line()
        if win_player is None:
            return
        for pos in win_line:
            self.field_buttons[pos].config(fg='green')
        time_passed = (datetime.now() - self.current_game_data.start_time).total_seconds()
        self.player_top_scores.add_new(win_player, time_passed)
        self.player_top_scores.render(self.window)
        self.player_top_scores.save('xo_top_scores.json')

    def update_window(self):
        self.window.after(66, lambda: self.update_window())
        if self.current_game_data.win_player_line()[0] is not None:
            return
        total_seconds = (datetime.now() - self.current_game_data.start_time).total_seconds()
        diff_time_str = datetime.fromtimestamp(total_seconds).strftime("%M:%S")
        self.game_time_label.configure(text=diff_time_str)


def main():
    game = Game()


if __name__ == '__main__':
    main()

