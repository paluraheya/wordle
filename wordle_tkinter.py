import tkinter as tk
from tkinter import messagebox
import random
from PIL import Image, ImageTk
from sound import *
import json
import os

class Wordle:
    MAX_ATTEMPTS = 6
    WORD_LENGTH = 5
    VOIDED_LETTER = "*"

    def __init__(self, secret):
        self.secret = secret.upper()
        self.attempts = []

    def attempt(self, word):
        self.attempts.append(word.upper())

    def guess(self, word):
        word = word.upper()
        result = [LetterState(x) for x in word]
        remaining_secret = list(self.secret)

        for i in range(self.WORD_LENGTH):
            if result[i].character == remaining_secret[i]:
                result[i].is_in_position = True
                remaining_secret[i] = self.VOIDED_LETTER

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


class LetterState:
    def __init__(self, character):
        self.character = character
        self.is_in_word = False
        self.is_in_position = False






class WordleApp:
    COLORS = {
        "green": "#6aaa64",
        "yellow": "#c9b458",
        "gray": "#787c7e",
        "dark-grey": "#3b3b3b",
        "empty": "#d3d6da",
        "bg": "#3a0ca3",
        "tile_text": "white",
        "key_default": "#818384"
    }

    STATS_FILE = "wordle_stats.json"

    def load_stats(self):
        if os.path.exists(self.STATS_FILE):
            try:
                with open(self.STATS_FILE, "r") as f:
                    return json.load(f)
            except:
                return {"wins": 0, "losses": 0}
        else:
            return {"wins": 0, "losses": 0}

    def save_stats(self):
        with open(self.STATS_FILE, "w") as f:
            json.dump(self.stats, f)

    def get_stats_message(self):
        wins = self.stats["wins"]
        losses = self.stats["losses"]
        total = wins + losses
        
        if total > 0:
            percentage = (wins / total) * 100
        else:
            percentage = 0
            
        return f"\nWins: {wins} | Losses: {losses}\nWin Rate: {percentage:.1f}%"
    

    def __init__(self, root):
        self.root = root
        self.stats = self.load_stats()
        self.root.title("Wordle")
        self.root.attributes("-fullscreen", True)
        def exit_fullscreen(event=None):
            self.root.attributes("-fullscreen", False)

        self.sound = SoundManager()
        self.sound.play_game_music()

        

        
        self.root.config(bg=self.COLORS["bg"])
        icon_image = tk.PhotoImage(file='images/Icon.png')
        self.root.iconphoto(True, icon_image)

        self.bg_canvas = tk.Canvas(self.root, width=1920, height=1080, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        bg = Image.open("images/bg_game.png")
        bg = bg.resize((screen_w, screen_h), Image.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(bg)

        self.bg_canvas.create_image(0, 0, anchor="nw", image=self.bg_img)

        screen_w = self.root.winfo_screenwidth()
        
        self.stats_text_id = self.bg_canvas.create_text(
            50, 250,         
            anchor="nw",              
            text="",                 
            font=("Clarendon BT", 18, "bold"),
            fill="white",
            justify="left"
        )
        
        self.update_stats_label()
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # load words
        try:
            with open("wordlist_upd.txt", "r") as f:
                self.words = [w.strip().upper() for w in f if len(w.strip()) == 5]
        except Exception:
            self.words = ["APPLE", "MANGO", "BERRY", "GRAPE", "LEMON"]

        self.secret = random.choice(self.words)
        self.wordle = Wordle(self.secret)
        self.current_guess = ""
        self.revealing = False

        self.tiles = []
        self.key_buttons = {}


        self.btn_back_img = tk.PhotoImage(file="images/back.png")
        self.back_btn = self.bg_canvas.create_image(100, 50, image=self.btn_back_img)
        self.bg_canvas.tag_bind(self.back_btn, "<Button-1>", self.back_menu)
        self.root.bind("<Escape>", self.back_menu)

        self.create_grid()
        self.create_keyboard()
        self.create_input_events()
        self.grid_frame.lift()
        self.keyboard_frame.lift()


    def update_stats_label(self):
        wins = self.stats.get("wins", 0)
        losses = self.stats.get("losses", 0)
        total = wins + losses
        percentage = (wins / total * 100) if total > 0 else 0
        
        display_text = f"Wins: {wins} | Losses: {losses}\nWin Rate: {percentage:.1f}%"
        
        self.bg_canvas.itemconfigure(self.stats_text_id, text=display_text)

    # grid
    def create_grid(self):
        self.grid_frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        self.grid_frame.pack(pady=30)
        for r in range(self.wordle.MAX_ATTEMPTS):
            row = []
            for c in range(self.wordle.WORD_LENGTH):
                lbl = tk.Label(
                    self.grid_frame,
                    text="",
                    font=("Clarendon BT", 28, "bold"),
                    width=2,
                    height=1,
                    bg=self.COLORS["bg"],
                    fg=self.COLORS["tile_text"],
                    relief="groove",
                    borderwidth=6
                )
                lbl.grid(row=r, column=c, padx=5, pady=5)
                row.append(lbl)
            self.tiles.append(row)

    # keyboard
    def create_keyboard(self):
        self.keyboard_frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        self.keyboard_frame.pack(pady=10)

        keyboard_rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        for r, keys in enumerate(keyboard_rows):
            row_frame = tk.Frame(self.keyboard_frame, bg=self.COLORS["bg"])
            row_frame.pack(pady=3)
            for k in keys:
                btn = tk.Button(
                    row_frame,
                    text=k,
                    width=4,
                    height=2,
                    font=("Clarendon BT", 12, "bold"),
                    bg=self.COLORS["key_default"],
                    fg="white",
                    activebackground="#565758",
                    command=lambda ch=k: self.key_press(ch)
                )
                btn.pack(side=tk.LEFT, padx=4)
                self.key_buttons[k] = btn  # save reference
            if r == 2:
                tk.Button(
                    row_frame, text="←", width=6, height=2,
                    font=("Clarendon BT", 12, "bold"),
                    bg=self.COLORS["key_default"], fg="white",
                    command=self.backspace
                ).pack(side=tk.LEFT, padx=3)
                tk.Button(
                    row_frame, text="ENTER", width=8, height=2,
                    font=("Clarendon BT", 12, "bold"),
                    bg="#538d4e", fg="white",
                    command=self.submit
                ).pack(side=tk.LEFT, padx=3)

    # events
    def create_input_events(self):
        self.root.bind("<Key>", self.on_key)

    def on_key(self, event):
        if self.revealing:
            return
        if event.keysym == "Return":
            self.submit()
        elif event.keysym == "BackSpace":
            self.backspace()
        elif event.char.isalpha() and len(event.char) == 1:
            self.key_press(event.char.upper())

    def key_press(self, t):
        if len(self.current_guess) < self.wordle.WORD_LENGTH and self.wordle.can_attempt and not self.revealing:
            row = len(self.wordle.attempts)
            lbl = self.tiles[row][len(self.current_guess)]
            lbl.config(text=t)
            self.current_guess += t

    def backspace(self):
        if len(self.current_guess) > 0 and not self.revealing:
            row = len(self.wordle.attempts)
            col = len(self.current_guess) - 1
            self.tiles[row][col].config(text="")
            self.current_guess = self.current_guess[:-1]

    # sumbit
    def submit(self):
        if self.revealing:
            return
        if len(self.current_guess) != self.wordle.WORD_LENGTH:
            return
        if self.current_guess not in self.words:
            self.warning()
            return

        self.wordle.attempt(self.current_guess)
        result = self.wordle.guess(self.current_guess)
        self.reveal_index = 0
        self.reveal_result = result
        self.revealing = True
        self._reveal_step()
        self.current_guess = ""


    def warning(self):
        popup = tk.Toplevel(self.root)
        popup.title("Invalid")

        
        popup.resizable(False, False)
        popup_width = 300
        popup_height = 200

        

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        x = (screen_w - popup_width) // 2
        y = (screen_h - popup_height) // 2

        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        popup.grab_set()
        popup.focus_force()

        bg = Image.open("images/bg_ins.png")
        bg = bg.resize((popup_width, popup_height), Image.LANCZOS)
        popup.bg_image = ImageTk.PhotoImage(bg)

        
        popup.canvas = tk.Canvas(popup, width=popup_width, height=popup_height, highlightthickness=0)
        popup.canvas.pack(fill="both", expand=True)

        popup.canvas.create_image(0, 0, anchor="nw", image=popup.bg_image)

        
        popup.canvas.create_text(
            popup_width//2, popup_height//2,
            text=f'The word "{self.current_guess}"\n' "is not on the list\n",
            font=("Clarendon BT", 22, "bold"),
            fill="white",
            justify="center"
        )

        

        popup.bind("<Escape>", lambda e: popup.destroy())
        popup.bind("<Return>", lambda e: popup.destroy())

    # reveal
    def _reveal_step(self):
        
        row = len(self.wordle.attempts) - 1
        i = self.reveal_index
        if i >= len(self.reveal_result):
            self.revealing = False
            if self.wordle.is_solved:
                self.stats["wins"] += 1
                self.save_stats()
                stats_msg = self.get_stats_message()
                self.won("You guessed it!\n" "Congratulations!!")
                
            elif not self.wordle.can_attempt:
                self.stats["losses"] += 1
                self.save_stats()
                stats_msg = self.get_stats_message()
                self.lost("Out of attempts\n" f'The word was "{self.wordle.secret}"\n')
            return

        letter_state = self.reveal_result[i]
        tile = self.tiles[row][i]
        tile_char = letter_state.character
        tile.config(text=tile_char)

        # determine color
        if letter_state.is_in_position:
            color = self.COLORS["green"]
        elif letter_state.is_in_word:
            color = self.COLORS["yellow"]
        else:
            color = self.COLORS["dark-grey"]

        # color the tile and keyboard key
        def apply_color():
            tile.config(bg=color, fg="white")
            self.update_key_color(tile_char, color)
            self.reveal_index += 1
            self.root.after(180, self._reveal_step)

        self.root.after(150, apply_color)

    # keyboard color
    def update_key_color(self, letter, color):
        btn = self.key_buttons.get(letter.upper())
        if not btn:
            return

        # Priority: green > yellow > gray
        current_color = btn.cget("bg")
        priority = {"green": 3, "yellow": 2, "dark-grey": 1, self.COLORS["key_default"]: 0}
        current_rank = priority.get(current_color, 0)
        new_rank = 3 if color == self.COLORS["green"] else 2 if color == self.COLORS["yellow"] else 1

        if new_rank > current_rank:
            btn.config(bg=color)

    def back_menu(self, event=None):
        try:
            self.grid_frame.pack_forget()
            self.keyboard_frame.pack_forget()
        except:
            pass
        from wordle_main_menu import MainMenu
        self.sound.stop_music()
        self.sound.play_menu_music()
        MainMenu(self.root)




    # end game
    def won(self, msg):
        popup = tk.Toplevel(self.root)
        popup.resizable(False, False)
        popup_width = 400
        popup_height = 300

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        x = (screen_w - popup_width) // 2
        y = (screen_h - popup_height) // 2

        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        popup.grab_set()
        popup.focus_force()

        bg = Image.open("images/bg_ins.png")
        bg = bg.resize((popup_width, popup_height), Image.LANCZOS)
        popup.bg_image = ImageTk.PhotoImage(bg)

        
        popup.canvas = tk.Canvas(popup, width=popup_width, height=popup_height, highlightthickness=0)
        popup.canvas.pack(fill="both", expand=True)

        popup.canvas.create_image(0, 0, anchor="nw", image=popup.bg_image)

        popup.canvas.create_text(
            popup_width//2, 100,
            text=msg,
            font=("Clarendon BT", 22, "bold"),
            fill="white",
            justify="center"
        )

        def close_popup(event=None):
            popup.destroy()
            self.back_menu()

        popup.btn_back_img = tk.PhotoImage(file="images/btn_main_menu.png")
        popup.back_btn = popup.canvas.create_image(popup_width//2, 230, image=popup.btn_back_img)
        popup.canvas.tag_bind(popup.back_btn, "<Button-1>", close_popup)


        popup.bind("<Escape>", lambda e: close_popup())
        popup.protocol("WM_DELETE_WINDOW", close_popup)

        self.sound.play("win")


    def lost(self, msg):
        popup = tk.Toplevel(self.root)
        popup.resizable(False, False)
        popup_width = 400
        popup_height = 300

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        x = (screen_w - popup_width) // 2
        y = (screen_h - popup_height) // 2

        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        popup.grab_set()
        popup.focus_force()

        bg = Image.open("images/bg_ins.png")
        bg = bg.resize((popup_width, popup_height), Image.LANCZOS)
        popup.bg_image = ImageTk.PhotoImage(bg)

        
        popup.canvas = tk.Canvas(popup, width=popup_width, height=popup_height, highlightthickness=0)
        popup.canvas.pack(fill="both", expand=True)

        popup.canvas.create_image(0, 0, anchor="nw", image=popup.bg_image)

        popup.canvas.create_text(
            popup_width//2, 120,
            text=msg,
            font=("Clarendon BT", 22, "bold"),
            fill="white",
            justify="center"
        )

        def close_popup(event=None):
            popup.destroy()
            self.back_menu()

        popup.btn_back_img = tk.PhotoImage(file="images/btn_main_menu.png")
        popup.back_btn = popup.canvas.create_image(popup_width//2, 230, image=popup.btn_back_img)
        popup.canvas.tag_bind(popup.back_btn, "<Button-1>", close_popup)

        self.sound.play("lose")


    


    def reset_game(self):
        self.revealing = False
        self.secret = random.choice(self.words)
        self.wordle = Wordle(self.secret)
        self.current_guess = ""
        self.reveal_index = 0
        self.reveal_result = []
        for row in self.tiles:
            for tile in row:
                tile.config(text="", bg=self.COLORS["bg"], fg=self.COLORS["tile_text"])
        for btn in self.key_buttons.values():
            btn.config(bg=self.COLORS["key_default"])
    
    

if __name__ == "__main__":
    root = tk.Tk()
    app = WordleApp(root)
    root.mainloop()
