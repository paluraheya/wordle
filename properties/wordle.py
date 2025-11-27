import random
from typing import List
from math import remainder
from colorama import Fore
import tkinter as tk
from tkinter import messagebox


class Wordle:

    MAX_ATTEMPTS = 6
    WORD_LENGTH = 5
    VOIDED_LETTER = "*"

    def __init__(self, secret: str):
        self.secret: str = secret.upper()
        self.attempts = []

    def attempt(self, word: str):
        word = word.upper()
        self.attempts.append(word)

    def guess(self, word: str):
        word = word.upper()

        result = [LetterState(x) for x in word]

        remaining_secret = list(self.secret)

        for i in range(self.WORD_LENGTH):
            letter = result[i]
            if letter.character == remaining_secret[i]:
                letter.is_in_position = True
                remaining_secret[i] = self.VOIDED_LETTER

        for i in range(self.WORD_LENGTH):
            letter = result[i]

            if letter.is_in_position:
                continue

            for j in range(self.WORD_LENGTH):
                if letter.character == remaining_secret[j]:
                    remaining_secret[j] = self.VOIDED_LETTER
                    letter.is_in_word = True
                    break

        return result

    @property
    def is_solved(self):
        return len(self.attempts) > 0 and self.attempts[-1] == self.secret

    @property
    def remaining_attempts(self) -> int:
        return self.MAX_ATTEMPTS - len(self.attempts)

    @property
    def can_attempt(self):
        return self.remaining_attempts > 0 and not self.is_solved

class LetterState:
    def __init__(self, character: str):
        self.character: str = character
        self.is_in_word: bool = False
        self.is_in_position: bool = False

    def __repr__(self):
        return f"[{self.character} is_in_word: {self.is_in_word} is_in_position: {self.is_in_position}]"






def main():
    word_set = load_word_set("wordle_words.txt")
    secret = random.choice(list(word_set))
    wordle = Wordle(secret)

    while wordle.can_attempt:
        x = input("\nType your guess: ")

        if len(x) != wordle.WORD_LENGTH:
            print(f"Word must be {wordle.WORD_LENGTH} characters long!")
            continue

        wordle.attempt(x)
        display_results(wordle)

    if wordle.is_solved:
        print("You've solved the puzzle.")
    else:
        print("You failed to solve the puzzle!")
        print(f"The secret word was: {wordle.secret}")


def display_results(wordle: Wordle):
    print("\nYour results so far...")
    print(f"You have {wordle.remaining_attempts} attempts remaining.\n")

    lines = []

    for word in wordle.attempts:
        result = wordle.guess(word)
        colored_result_str = convert_result_to_color(result)
        lines.append(colored_result_str)

    for _ in range(wordle.remaining_attempts):
        lines.append(" ".join(["_"] * wordle.WORD_LENGTH))

    draw_border_around(lines)


def load_word_set(path: str):
    word_set = set()
    with open(path, "r") as f:
        for line in f.readlines():
            word = line.strip().upper()
            word_set.add(word)
    return word_set


def convert_result_to_color(result: List[LetterState]):
    result_with_color = []
    for letter in result:
        if letter.is_in_position:
            color = Fore.GREEN
        elif letter.is_in_word:
            color = Fore.YELLOW
        else:
            color = Fore.WHITE
        colored_letter = color + letter.character + Fore.RESET
        result_with_color.append(colored_letter)
    return " ".join(result_with_color)


def draw_border_around(lines: List[str], size: int = 9, pad: int = 1):

    content_length = size + pad * 2
    top_border = "┌" + "─" * content_length + "┐"
    bottom_border = "└" + "─" * content_length + "┘"
    space = " " * pad
    print(top_border)

    for line in lines:
        print("│" + space + line + space + "│")

    print(bottom_border)


if __name__ == "__main__":
    main()




