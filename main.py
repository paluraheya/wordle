import tkinter as tk
from wordle_tkinter import *
from PIL import Image, ImageTk
from sound import *

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Wordle Menu")
        self.root.attributes("-fullscreen", True)
        def exit_fullscreen(event=None):
            self.root.attributes("-fullscreen", False)
        self.root.bind("<Escape>", exit_fullscreen)

        self.sound = SoundManager()
        self.sound.play_menu_music()


        self.canvas = tk.Canvas(root, width=1920, height=1080, highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        bg = Image.open("images/bg_fix.png")
        bg = bg.resize((screen_w, screen_h), Image.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(bg)

        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_img)

        self.btn_play_img = tk.PhotoImage(file="images/btn_play.png")
        self.btn_instr_img = tk.PhotoImage(file="images/btn_instruction.png")
        self.btn_exit_img = tk.PhotoImage(file="images/btn_exit.png")

        center_x = self.root.winfo_screenwidth() // 2
        self.play_btn = self.canvas.create_image(center_x, 270, image=self.btn_play_img)
        self.instr_btn = self.canvas.create_image(center_x, 390, image=self.btn_instr_img)
        self.exit_btn = self.canvas.create_image(center_x, 510, image=self.btn_exit_img)


        self.canvas.tag_bind(self.play_btn, "<Button-1>", self.start_game)
        self.canvas.tag_bind(self.instr_btn, "<Button-1>", self.show_instructions)
        self.canvas.tag_bind(self.exit_btn, "<Button-1>", self.exit_game)

    
    def start_game(self, event=None):
        self.canvas.place_forget()
        self.sound.stop_music()
        WordleApp(self.root)
        self.sound.play_game_music()

    def show_instructions(self, event=None):
        self.open_instruction_window()

    def exit_game(self, event=None):
        self.root.quit()

    def open_instruction_window(self):
        popup = tk.Toplevel(self.root)
        popup.title("How to Play")

        
        popup.resizable(False, False)
        popup_width = 800
        popup_height = 600

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        x = (screen_w - popup_width) // 2
        y = (screen_h - popup_height) // 2

        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        bg = Image.open("images/bg_ins.png")
        bg = bg.resize((popup_width, popup_height), Image.LANCZOS)
        popup.bg_image = ImageTk.PhotoImage(bg)

        
        popup.canvas = tk.Canvas(popup, width=popup_width, height=popup_height, highlightthickness=0)
        popup.canvas.pack(fill="both", expand=True)

        popup.canvas.create_image(0, 0, anchor="nw", image=popup.bg_image)

        instruction_text = (
                "Wordle is a word-guessing game where you must identify a secret\n"
                "five-letter word within six attempts. After each guess, the game\n"
                "provides color-coded feedback to help you refine your next guesses.\n\n"
                "1. Enter a five-letter word as your first attempt.\n"
                "    The word must be a valid dictionary entry.\n\n"
                "2. Observe the color changes on each letter after submitting\n"
                "    your guess. These colors act as clues:\n\n"
                "    Green  : Correct letter in the correct position.\n"
                "    Yellow : Correct letter but wrong position.\n"
                "    Gray   : Letter does not appear in the secret word.\n\n"
                "3. Use these clues wisely: keep greens, move yellows,\n"
                "    and avoid grays in future guesses.\n\n"
                "4. Continue guessing until you find the secret word or\n"
                "    run out of attempts. The game ends when you win or\n"
                "    after six tries.\n"
            )




        popup.canvas.create_text(
            popup_width//2, 40,
            text="WORDLE RULES",
            font=("Clarendon BT", 30, "bold"),
            fill="white"
        )

        popup.canvas.create_text(
            popup_width//2, 300,
            text=instruction_text,
            font=("Times New Roman", 14),
            fill="white"
        )


        popup.btn_next = tk.PhotoImage(file="images/btn_next.png")
        popup.next_btn = popup.canvas.create_image(700, 500, image=popup.btn_next)
        popup.canvas.tag_bind(popup.next_btn, "<Button-1>", lambda e: self.next(popup))
        

        self.root.bind("<Escape>", lambda e: popup.destroy())


    def next(self, prev_popup):
        prev_popup.destroy()
        
        popup = tk.Toplevel(self.root)
        popup.title("How to Play")

        
        popup.resizable(False, False)
        popup_width = 800
        popup_height = 600

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        x = (screen_w - popup_width) // 2
        y = (screen_h - popup_height) // 2

        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        bg = Image.open("images/bg_ins.png")
        bg = bg.resize((popup_width, popup_height), Image.LANCZOS)
        popup.bg_image = ImageTk.PhotoImage(bg)

        
        popup.canvas = tk.Canvas(popup, width=popup_width, height=popup_height, highlightthickness=0)
        popup.canvas.pack(fill="both", expand=True)

        popup.canvas.create_image(0, 0, anchor="nw", image=popup.bg_image)


        popup.canvas.create_text(
            popup_width//2, 40,
            text="WORDLE RULES",
            font=("Clarendon BT", 30, "bold"),
            fill="white"
        )

        popup.canvas.create_text(
            popup_width//2, 100,
            text="Example",
            font=("Clarendon BT", 24, "bold"),
            fill="#abc7cc"
        )

        popup.canvas.create_text(
            550, 170,
            text='E is correct letter but at the wrong Position.',
            font=("Clarendon BT", 12, "bold"),
            fill="#abc7cc"
        )

        popup.canvas.create_text(
            560, 270,
            text='E is correct letter but at the wrong Position.\n' 'S and P is the correct letter at correct Position. ',
            font=("Clarendon BT", 12, "bold"),
            fill="#abc7cc"
        )

        popup.canvas.create_text(
            560, 370,
            text="All letters is correct and at the correct Position.\n" "That means we already found the Secret Word.",
            font=("Clarendon BT", 12, "bold"),
            fill="#abc7cc"
        )

        popup.ins_1 = tk.PhotoImage(file="images/ins_1.png")
        popup.inst_1 = popup.canvas.create_image(200, 170, image=popup.ins_1)

        popup.ins_2 = tk.PhotoImage(file="images/ins_2.png")
        popup.inst_2 = popup.canvas.create_image(200, 270, image=popup.ins_2)

        popup.ins_3 = tk.PhotoImage(file="images/ins_3.png")
        popup.inst_3 = popup.canvas.create_image(200, 370, image=popup.ins_3)

        popup.btn_close = tk.PhotoImage(file="images/close.png")
        popup.close_btn = popup.canvas.create_image(700, 500, image=popup.btn_close)
        popup.canvas.tag_bind(popup.close_btn, "<Button-1>", lambda e: popup.destroy())

        self.root.bind("<Escape>", lambda e: popup.destroy())



if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()

