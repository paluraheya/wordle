# wordle_single_file.py
import tkinter as tk
from tkinter import messagebox
import random
import json
import os

# -------------------------
# persistence for stats
# -------------------------
STATS_PATH = "stats.json"

def load_stats():
    if not os.path.exists(STATS_PATH):
        return {
            "games_played": 0,
            "games_won": 0,
            "current_streak": 0,
            "best_streak": 0,
            "distribution": [0,0,0,0,0,0]  # guesses 1..6
        }
    try:
        with open(STATS_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {
            "games_played": 0,
            "games_won": 0,
            "current_streak": 0,
            "best_streak": 0,
            "distribution": [0,0,0,0,0,0]
        }

def save_stats(stats):
    with open(STATS_PATH, "w") as f:
        json.dump(stats, f)

# -------------------------
# Wordle game logic
# -------------------------
class LetterState:
    def __init__(self, character):
        self.character = character
        self.is_in_word = False
        self.is_in_position = False

class Wordle:
    MAX_ATTEMPTS = 6
    WORD_LENGTH = 5
    VOIDED_LETTER = "*"

    def __init__(self, secret: str):
        self.secret = secret.upper()
        self.attempts = []

    def attempt(self, word: str):
        self.attempts.append(word.upper())

    def guess(self, word: str):
        word = word.upper()
        result = [LetterState(x) for x in word]
        remaining_secret = list(self.secret)

        # mark greens first
        for i in range(self.WORD_LENGTH):
            if result[i].character == remaining_secret[i]:
                result[i].is_in_position = True
                remaining_secret[i] = self.VOIDED_LETTER

        # mark yellows
        for i in range(self.WORD_LENGTH):
            if result[i].is_in_position:
                continue
            for j in range(self.WORD_LENGTH):
                if result[i].character == remaining_secret[j]:
                    result[i].is_in_word = True
                    remaining_secret[j] = self.VOIDED_LETTER
                    break

        return result

    @property
    def is_solved(self):
        return len(self.attempts) > 0 and self.attempts[-1] == self.secret

    @property
    def remaining_attempts(self):
        return self.MAX_ATTEMPTS - len(self.attempts)

    @property
    def can_attempt(self):
        return self.remaining_attempts > 0 and not self.is_solved

# -------------------------
# UI app (menu, game, stats)
# -------------------------
class App:
    COLORS = {
        "bg": "#121213",
        "tile_text": "white",
        "green": "#6aaa64",
        "yellow": "#c9b458",
        "gray": "#787c7e",
        "key_white": "white",
        "key_black": "black",
        "panel": "#181818"
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Wordle - Single File")
        # set icon if exists
        try:
            icon = tk.PhotoImage(file="Icon.png")
            self.root.iconphoto(True, icon)
        except Exception:
            pass

        self.root.configure(bg=self.COLORS["bg"])
        self.root.resizable(False, False)

        # load words
        self.word_list = self.load_word_list()

        # load stats
        self.stats = load_stats()

        # frames
        self.current_frame = None

        # show menu
        self.show_menu()

        # ensure key events go to root
        self.root.bind("<Key>", lambda e: None)  # placeholder to ensure key system active

    def load_word_list(self):
        fname = "wordlist.txt"
        try:
            with open(fname, "r") as f:
                words = [w.strip().upper() for w in f if len(w.strip()) == 5]
                return words if words else ["APPLE","MANGO","BERRY","GRAPE","LEMON"]
        except Exception:
            return ["APPLE","MANGO","BERRY","GRAPE","LEMON"]

    # -------------------------
    # Utilities
    # -------------------------
    def clear_frame(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

    def center_root(self, w=420, h=680):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w)//2
        y = (sh - h)//3
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # -------------------------
    # MENU
    # -------------------------
    def show_menu(self):
        self.clear_frame()
        self.center_root()
        frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

        # attempt to load background image
        try:
            bg_img = tk.PhotoImage(file="menu_bg.png")
            canvas = tk.Canvas(frame, width=420, height=680, highlightthickness=0)
            canvas.pack()
            canvas.create_image(0, 0, anchor="nw", image=bg_img)
            canvas.image = bg_img  # keep ref
            # try load buttons images
            try:
                play_img = tk.PhotoImage(file="btn_play.png")
                stats_img = tk.PhotoImage(file="btn_stats.png")
                exit_img = tk.PhotoImage(file="btn_exit.png")
                play = canvas.create_image(210, 360, image=play_img)
                stats = canvas.create_image(210, 440, image=stats_img)
                ex = canvas.create_image(210, 520, image=exit_img)
                canvas.image_play = play_img
                canvas.image_stats = stats_img
                canvas.image_exit = exit_img
                canvas.tag_bind(play, "<Button-1>", lambda e: self.show_game())
                canvas.tag_bind(stats, "<Button-1>", lambda e: self.show_stats())
                canvas.tag_bind(ex, "<Button-1>", lambda e: self.root.quit())
            except Exception:
                # fallback to simple buttons overlaying the canvas
                btn_play = tk.Button(frame, text="Play", width=20, height=2, command=self.show_game)
                btn_stats = tk.Button(frame, text="Stats", width=20, height=2, command=self.show_stats)
                btn_exit = tk.Button(frame, text="Exit", width=20, height=2, command=self.root.quit)
                btn_play.place(x=120, y=340)
                btn_stats.place(x=120, y=420)
                btn_exit.place(x=120, y=500)
        except Exception:
            # no background image; simple menu
            title = tk.Label(frame, text="WORDLE", font=("Helvetica", 28, "bold"), bg=self.COLORS["bg"], fg="white")
            title.pack(pady=(40, 10))
            sub = tk.Label(frame, text="Tkinter Edition", bg=self.COLORS["bg"], fg="white")
            sub.pack(pady=(0,20))
            tk.Button(frame, text="Play", width=20, height=2, command=self.show_game).pack(pady=12)
            tk.Button(frame, text="Stats", width=20, height=2, command=self.show_stats).pack(pady=8)
            tk.Button(frame, text="Exit", width=20, height=2, command=self.root.quit).pack(pady=8)

        # show total solved on menu
        done = self.stats.get("games_won", 0)
        lbl = tk.Label(frame, text=f"Total Solved: {done}", bg=self.COLORS["bg"], fg="white", font=("Helvetica", 12, "bold"))
        lbl.pack(side="bottom", pady=12)

    # -------------------------
    # STATS SCREEN
    # -------------------------
    def show_stats(self):
        self.clear_frame()
        self.center_root(560, 480)
        frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

        s = self.stats
        played = s.get("games_played", 0)
        won = s.get("games_won", 0)
        perc = int((won / played) * 100) if played > 0 else 0
        curr = s.get("current_streak", 0)
        best = s.get("best_streak", 0)
        dist = s.get("distribution", [0,0,0,0,0,0])

        tk.Label(frame, text="Statistics", font=("Helvetica", 20, "bold"), bg=self.COLORS["bg"], fg="white").pack(pady=8)
        info_frame = tk.Frame(frame, bg=self.COLORS["panel"])
        info_frame.pack(pady=8, padx=12, fill="x")

        def info_label(parent, title, value):
            f = tk.Frame(parent, bg=self.COLORS["panel"])
            tk.Label(f, text=title, bg=self.COLORS["panel"], fg="white", font=("Helvetica", 10)).pack()
            tk.Label(f, text=value, bg=self.COLORS["panel"], fg="white", font=("Helvetica", 14, "bold")).pack()
            return f

        row = tk.Frame(info_frame, bg=self.COLORS["panel"])
        row.pack(padx=8, pady=8, fill="x")
        info_label(row, "Played", played).pack(side="left", expand=True, padx=8)
        info_label(row, "Win %", f"{perc}%").pack(side="left", expand=True, padx=8)
        info_label(row, "Current Streak", curr).pack(side="left", expand=True, padx=8)
        info_label(row, "Best Streak", best).pack(side="left", expand=True, padx=8)

        # Distribution bars
        bar_frame = tk.Frame(frame, bg=self.COLORS["bg"])
        bar_frame.pack(pady=8)
        tk.Label(bar_frame, text="Guess Distribution", bg=self.COLORS["bg"], fg="white").pack()
        maxv = max(dist) if any(dist) else 1
        for i, v in enumerate(dist, start=1):
            rowf = tk.Frame(bar_frame, bg=self.COLORS["bg"])
            rowf.pack(fill="x", padx=18, pady=3)
            tk.Label(rowf, text=str(i), width=2, bg=self.COLORS["bg"], fg="white").pack(side="left")
            bar_len = int((v / maxv) * 300) if maxv else 0
            bar = tk.Frame(rowf, bg=self.COLORS["green"], width=bar_len, height=18)
            bar.pack(side="left", padx=(6,6))
            tk.Label(rowf, text=str(v), bg=self.COLORS["bg"], fg="white").pack(side="left", padx=8)

        tk.Button(frame, text="Back to Menu", command=self.show_menu).pack(pady=12)

    # -------------------------
    # GAME
    # -------------------------
    def show_game(self):
        self.clear_frame()
        self.center_root()
        frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

        # game instance
        secret = random.choice(self.word_list)
        self.game = Wordle(secret)

        # UI elements
        header = tk.Frame(frame, bg=self.COLORS["bg"])
        header.pack(pady=(8,0))
        tk.Label(header, text="Wordle", font=("Helvetica", 18, "bold"), bg=self.COLORS["bg"], fg="white").pack(side="left", padx=8)
        self.record_label = tk.Label(header, text=f"Solved: {self.stats.get('games_won', 0)}", bg=self.COLORS["bg"], fg="white")
        self.record_label.pack(side="right", padx=8)

        # grid
        self.tiles = []
        grid_frame = tk.Frame(frame, bg=self.COLORS["bg"])
        grid_frame.pack(pady=12)
        for r in range(Wordle.MAX_ATTEMPTS):
            row = []
            for c in range(Wordle.WORD_LENGTH):
                lbl = tk.Label(grid_frame, text="", font=("Helvetica", 26, "bold"),
                               width=2, height=1, bg=self.COLORS["bg"], fg=self.COLORS["tile_text"],
                               relief="groove", borderwidth=2)
                lbl.grid(row=r, column=c, padx=6, pady=6)
                row.append(lbl)
            self.tiles.append(row)

        # keyboard (buttons stored)
        self.keys = {}
        kb_frame = tk.Frame(frame, bg=self.COLORS["bg"])
        kb_frame.pack(pady=8)
        rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        for i, keys in enumerate(rows):
            rowf = tk.Frame(kb_frame, bg=self.COLORS["bg"])
            rowf.pack(pady=2)
            for ch in keys:
                b = tk.Button(rowf, text=ch, font=("Helvetica", 11, "bold"),
                              width=4, height=2, bg=self.COLORS["key_white"], fg=self.COLORS["key_black"],
                              command=lambda ch=ch: self.key_press(ch))
                b.pack(side="left", padx=3)
                self.keys[ch] = b
            if i == 2:
                tk.Button(rowf, text="←", width=4, height=2, command=self.backspace).pack(side="left", padx=4)
                tk.Button(rowf, text="ENTER", width=6, height=2, bg=self.COLORS["green"], fg="white", command=self.submit).pack(side="left", padx=6)

        # state variables used during game
        self.current_guess = ""
        self.revealing = False
        self.reveal_index = 0
        self.reveal_result = None

        # bind keyboard to root and set focus
        self.root.bind("<Key>", self.on_key)
        self.root.focus_set()

    # input handlers
    def on_key(self, event):
        if self.revealing:
            return
        if event.keysym == "Return":
            self.submit()
        elif event.keysym == "BackSpace":
            self.backspace()
        elif event.char.isalpha() and len(event.char) == 1:
            self.key_press(event.char.upper())

    def key_press(self, ch):
        if not hasattr(self, "game"):
            return
        if len(self.current_guess) < Wordle.WORD_LENGTH and self.game.can_attempt:
            row = len(self.game.attempts)
            lbl = self.tiles[row][len(self.current_guess)]
            lbl.config(text=ch)
            self.current_guess += ch

    def backspace(self):
        if not hasattr(self, "game"):
            return
        if len(self.current_guess) > 0 and not self.revealing:
            row = len(self.game.attempts)
            col = len(self.current_guess) - 1
            self.tiles[row][col].config(text="")
            self.current_guess = self.current_guess[:-1]

    def submit(self):
        if not hasattr(self, "game") or self.revealing:
            return
        if len(self.current_guess) != Wordle.WORD_LENGTH:
            return
        if self.current_guess not in self.word_list:
            self.simple_popup(f"'{self.current_guess}' not in word list", color="#c0392b")
            return

        self.game.attempt(self.current_guess)
        result = self.game.guess(self.current_guess)
        self.reveal_result = result
        self.reveal_index = 0
        self.revealing = True
        # start reveal
        self._reveal_step()

    def _reveal_step(self):
        row = len(self.game.attempts) - 1
        if self.reveal_index >= Wordle.WORD_LENGTH:
            # done revealing row
            self.revealing = False
            if self.game.is_solved:
                self.on_win()
            elif not self.game.can_attempt:
                self.on_loss()
            self.current_guess = ""
            return

        letter_state = self.reveal_result[self.reveal_index]
        tile = self.tiles[row][self.reveal_index]
        tile_char = letter_state.character
        tile.config(text=tile_char)

        # choose color
        if letter_state.is_in_position:
            color = self.COLORS["green"]
        elif letter_state.is_in_word:
            color = self.COLORS["yellow"]
        else:
            color = self.COLORS["gray"]

        def apply_color():
            tile.config(bg=color, fg="white")
            self.update_key_color(tile_char, color)
            self.reveal_index += 1
            self.root.after(200, self._reveal_step)

        # small delay before applying color (animation feel)
        self.root.after(120, apply_color)

    def update_key_color(self, letter, color):
        btn = self.keys.get(letter.upper())
        if not btn:
            return
        # priority: green > yellow > gray > white
        current = btn.cget("bg")
        # map color to rank
        def rank(c):
            if c == self.COLORS["green"]: return 3
            if c == self.COLORS["yellow"]: return 2
            if c == self.COLORS["gray"]: return 1
            return 0
        if rank(color) >= rank(current):
            btn.config(bg=color, fg="white")

    # game result handlers
    def on_win(self):
        # update stats
        self.stats["games_played"] = self.stats.get("games_played", 0) + 1
        self.stats["games_won"] = self.stats.get("games_won", 0) + 1
        self.stats["current_streak"] = self.stats.get("current_streak", 0) + 1
        if self.stats["current_streak"] > self.stats.get("best_streak", 0):
            self.stats["best_streak"] = self.stats["current_streak"]
        # distribution: number of guesses used
        guesses_used = len(self.game.attempts)
        if 1 <= guesses_used <= 6:
            self.stats["distribution"][guesses_used-1] += 1
        save_stats(self.stats)
        self.record_label.config(text=f"Solved: {self.stats.get('games_won', 0)}")
        self.simple_popup("You guessed it! 🎉", color=self.COLORS["green"], end=True)

    def on_loss(self):
        self.stats["games_played"] = self.stats.get("games_played", 0) + 1
        self.stats["current_streak"] = 0
        save_stats(self.stats)
        self.simple_popup(f"You lost! Word was {self.game.secret}", color="#c0392b", end=True)

    # popup helper (small centered rectangle)
    def simple_popup(self, message, color="#333", end=False):
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.configure(bg=color)
        w, h = 300, 110
        # position center of root
        x = self.root.winfo_x() + (self.root.winfo_width()//2 - w//2)
        y = self.root.winfo_y() + (self.root.winfo_height()//2 - h//2)
        popup.geometry(f"{w}x{h}+{x}+{y}")
        tk.Label(popup, text=message, bg=color, fg="white", font=("Helvetica", 14, "bold")).pack(expand=True, fill="both", pady=15, padx=10)

        def close():
            popup.destroy()
            if end:
                self.post_game_prompt()
        popup.after(1600, close)

    def post_game_prompt(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Play Again?")
        dialog.transient(self.root)
        dialog.resizable(False, False)
        w, h = 300, 140
        x = self.root.winfo_x() + (self.root.winfo_width()//2 - w//2)
        y = self.root.winfo_y() + (self.root.winfo_height()//2 - h//2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        tk.Label(dialog, text="Play again?", font=("Helvetica", 13, "bold")).pack(pady=12)
        f = tk.Frame(dialog); f.pack()
        tk.Button(f, text="Yes", width=10, bg=self.COLORS["green"], fg="white", command=lambda: [dialog.destroy(), self.show_game()]).pack(side="left", padx=8)
        tk.Button(f, text="No", width=10, bg=self.COLORS["gray"], fg="white", command=lambda: [dialog.destroy(), self.show_menu()]).pack(side="left", padx=8)

# -------------------------
# Run app
# -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
