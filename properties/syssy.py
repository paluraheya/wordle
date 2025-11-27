import sys
import random # We'll need this for the game
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtCore import Qt

# --- 1. IMPORT YOUR GENERATED UI CLASS ---
# Your file is 'guigui.py', so the class inside is 'Ui_MainWindow'
# (Or whatever you named the window in Designer, default is MainWindow)
from guigui import Ui_MainWindow 

# --- 2. YOUR WORD LIST ---
# Go find a 5-letter word list text file, save it in this folder
try:
    with open("word_list.txt", "r") as f:
        WORD_LIST = set(line.strip().upper() for line in f)
except FileNotFoundError:
    print("WARNING: word_list.txt not found. Using tiny fallback list.")
    WORD_LIST = {"PYTHON", "GAMES", "WORLD", "HELLO", "PROXY"}


# --- 3. CREATE YOUR ACTUAL APPLICATION CLASS ---
class WordleWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- 4. SET UP THE UI (FROM YOUR GENERATED FILE) ---
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # --- 5. GAME LOGIC AND SETUP ---
        self.current_row = 0
        self.secret_word = random.choice(list(WORD_LIST))
        print(f"Secret word (for debugging): {self.secret_word}")

        # --- 6. CONNECT YOUR BUTTONS ---
        # We named them 'guess_button' and 'guess_input' in the .ui file
        self.ui.guess_button.clicked.connect(self.process_guess)
        self.ui.guess_input.returnPressed.connect(self.process_guess) # For hitting Enter
        
        # --- 7. CLEAR THE BOARD (SET LABELS BLANK) ---
        for r in range(6):
            for c in range(5):
                # This is why we named them 'box_0_0' etc.
                tile = self.findChild(QLabel, f"box_{r}_{c}")
                if tile:
                    tile.setText("") # Clear the 'A's you left

    # --- 8. YOUR GAME FUNCTIONS ---
    def process_guess(self):
        guess = self.ui.guess_input.text().upper()

        # --- Validation ---
        if len(guess) != 5:
            self.ui.message_label.setText("Guess must be 5 letters!")
            return
        if guess not in WORD_LIST:
            self.ui.message_label.setText("Not a valid word!")
            return
            
        # --- Check the letters ---
        for c, letter in enumerate(guess):
            # Find the label for this tile
            tile = self.findChild(QLabel, f"box_{self.current_row}_{c}")
            tile.setText(letter)
            
            # Apply colors
            if letter == self.secret_word[c]:
                # Green
                tile.setStyleSheet("background-color: #538d4e; border: 2px solid #565758; color: white;")
            elif letter in self.secret_word:
                # Yellow
                tile.setStyleSheet("background-color: #b59f3b; border: 2px solid #565758; color: white;")
            else:
                # Gray (already is, but good to be sure)
                tile.setStyleSheet("background-color: #3a3a3c; border: 2px solid #565758; color: white;")

        # --- Check for win/lose ---
        if guess == self.secret_word:
            self.ui.message_label.setText("You win!")
            self.ui.guess_input.setDisabled(True)
            self.ui.guess_button.setDisabled(True)
            return

        self.current_row += 1
        
        if self.current_row == 6:
            self.ui.message_label.setText(f"You lose! The word was {self.secret_word}")
            self.ui.guess_input.setDisabled(True)
            self.ui.guess_button.setDisabled(True)
            return

        # Clear input for next guess
        self.ui.guess_input.clear()
        self.ui.message_label.setText(f"Guess {self.current_row + 1}")


# --- 9. THE PART THAT ACTUALLY RUNS THE APP ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = WordleWindow()
    window.show()
    
    sys.exit(app.exec())