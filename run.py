from random import randrange
import os
from pyfiglet import Figlet
from termcolor import colored
import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("hangman_categories")
CATEGORIES = SHEET.worksheet("categories")


def game_title():
    """
    Clears the console and displays the game title
    """
    os.system('cls||clear')
    f = Figlet(font='big')
    title = f.renderText("HANGMAN") + "Created by Thomas Faulkner | Code Institute Python Project\n"
    colored_title = colored(title, on_color="on_blue")
    print(colored_title)


def select_difficluty():
    """
    Request for user to select game difficulty: Hard (5 Lives),
    Medium (6 Lives), Easy (7 Lives)
    """
    while True:
        print("Please select your game difficulty.\n")

        game_difficulty = {"Hard": 5, "Medium": 6, "Easy": 7}

        num = 1

        for difficulty, lives in game_difficulty.items():
            print(f"{num} - {difficulty} ({lives} Lives)")
            num += 1

        print("")
        input_value = input("Which difficulty would you like to select (1-3)? ")

        if validate_data(input_value, 3):
            break

    input_value = int(input_value)

    input_value -= 1

    difficulty = list(game_difficulty)[input_value]
    lives = list(game_difficulty.values())[input_value]

    game_title()
    print(f"You have selected game difficulty {difficulty} and will have {lives} lives.\n")

    return lives


def select_category():
    """
    Request for user to select the game category or for a random category to
    be chosen
    """
    while True:
        print("Please select one of the following categories, or choose 'Random' if you would like us to pick one for you.\n")

        data = CATEGORIES.get_all_values()
        categories_row = data[0]

        num = 1

        for category in categories_row:
            print(f"{num} - {category}")
            num += 1

        print(f"{num} - Random\n")

        num_of_categories = len(categories_row) + 1

        category_input = input(f"Which category number would you like to select (1-{num_of_categories})? ")

        if validate_data(category_input, num_of_categories):
            break

    category_input = int(category_input)

    category_column = category_input - 1

    if category_input <= len(categories_row):
        game_title()
        category = categories_row[category_column]
        print(f"You have chosen to guess something related to:\n")
    else:
        category_column = randrange((len(categories_row)))
        category = categories_row[category_column]
        game_title()
        print(f"The random category selected for you is {category}.\n")

    category_column += 1

    return category_column, category


def validate_data(value, num_of_options):
    """
    Inside the try checks whether an interger has been entered and
    whether it is within the range of the number of options.
    Raises ValueError or IndexError as appropriate.
    """

    try:
        int(value)

        if int(value) > num_of_options:
            raise IndexError(
                f"Please enter a value between 1-{num_of_options}. You entered '{value}'"
            )

    except ValueError as e:
        game_title()
        print(f"ValueError: {e}. Please enter a value between 1-{num_of_options}.\n")
        return False

    except IndexError as e:
        game_title()
        print(f"IndexError: {e}.\n")
        return False

    return True


def retrieve_word(column):
    """
    Retrieve word, phrase or sentence from the selected category column
    """
    column_values = CATEGORIES.col_values(column)
    column_values.pop(0)
    rand_column_cell = randrange((len(column_values)))
    game_word = column_values[rand_column_cell]

    final_game_word = []

    for letter in list(game_word):
        if letter == " ":
            letter = "/"
            final_game_word.append(letter)
        else:
            final_game_word.append(letter)

    game_word = ''.join(final_game_word)

    return game_word


def hide_game_word(game_word):
    """
    Change the game word into dashes (-, letters) and slashes (/, spaces)
    ready for the player to guess
    """
    game_word_split = list(game_word)

    hide_word = []

    for letter in game_word_split:
        if letter != "/":
            letter = "-"
            hide_word.append(letter)
        else:
            hide_word.append("/")

    hidden_game_word = ""

    for letter in hide_word:
        hidden_game_word += letter

    return hidden_game_word


class Game:
    """
    Main game play class
    """
    # Class variable
    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

    def __init__(self, letter_guess, game_word, hidden_game_word, lives, category):
        self.letter_guess = letter_guess
        self.game_word = game_word
        self.hidden_game_word = hidden_game_word
        self.lives = lives
        self.category = category

    def check_game_word(self):
        """
        Checks if the letter guessed is in the game word: returns true or false
        """
        if self.letter_guess in list(self.game_word) and self.letter_guess in Game.alphabet:
            return True
        else:
            return False

    def change_hidden_letter(self):
        """
        Makes the guessed letter appear in the hidden game word
        """
        list_index = 0
        hidden_word_list = list(self.hidden_game_word)

        for letter in self.game_word:

            if letter == self.letter_guess:
                hidden_word_list[list_index] = self.letter_guess.upper()

            list_index += 1

        self.hidden_game_word = ''.join(hidden_word_list)
        return self.hidden_game_word

    def remove_letter_guess(self):
        """
        Removes the guessed letter from the  alphabet
        so it can not be guessed again
        """
        Game.alphabet.remove(self.letter_guess)
        return Game.alphabet

    def remove_life(self):
        """
        Removes life if an incorrect guess has been made
        """
        self.lives -= 1
        return self.lives


def reset_game():
    """
    Requests if player wants to reset another game or quit
    """
    reset = input("Would you like to play again (y/n): ")

    if reset.lower() == "y":
        Game.alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
        main()
    else:
        game_title()
        print("Thank you for playing Hangman. We hope you had fun!!! Come back soon.\n")


def display_game_word(game_word):
    """
    Changes the "/" in the game word to spaces, and capitalizes each the first letter of each word
    """
    game_word = game_word.title()

    display_word = []

    for letter in game_word:
        if letter == "/":
            display_word.append(" ")
        else:
            display_word.append(letter)

    display_word = ''.join(display_word)

    return display_word


def game_won(game_word, lives, category, hidden_game_word, alphabet):
    """
    
    """
    game_title()

    game_word = display_game_word(game_word)
    print(f"Congratulations!!! You have guessed the correct answer which was {game_word}, with {lives} lives remaining.\n")

    print(f"{category}\n")
    print(f"{hidden_game_word}\n")

    display_alphabet = ''.join(alphabet)
    print(f"Remaining letters: {display_alphabet.upper()}\n")

    reset_game()


def play_game(game_word, hidden_game_word, lives, category):
    """
    Main game play
    Checks whether game won, lost or to continue
    """
    while True:
        game = Game("", game_word, hidden_game_word, lives, category)

        print(f"{game.category}\n")
        print(f"{game.hidden_game_word}\n")

        display_alphabet = ''.join(game.alphabet)
        print(f"Remaining letters: {display_alphabet.upper()}\n")

        letter_guess = input("Select a letter from the remaining in the letters above: ")

        # Guess Game Word Feature: if a string more than 3 letters is input, 
        # the following treats it as a guess and checks if it is equal to the game word.
        # Removes a life if the guess is incorrect

        if len(letter_guess) > 3:
            if letter_guess.title() == display_game_word(game.game_word):
                game_won(game.game_word, game.lives, game.category, game.hidden_game_word, game.alphabet)
                return None
            else:
                game.remove_life()

            if game.lives > 0:
                game_title()
                print(f"You guessed that the answer is '{letter_guess}' which is incorrect. You have {game.lives} lives remaining.\n")
                play_game(game.game_word, game.hidden_game_word, game.lives, game.category)
            else:
                game_title()
                game_word = display_game_word(game.game_word)
                print(f"You guessed that the answer is '{letter_guess}' which is incorrect. You have 0 lives remaining. The answer which you was trying to guess was {game_word}.\n")
                print(f"{game.category}\n")
                print(f"{game.hidden_game_word}")
                print(f"Remaining letters: {display_alphabet.upper()}\n")
                reset_game()

        elif validate_letter(letter_guess, game.alphabet):
            break

    print("") # Poosibly Delete
    game.letter_guess = letter_guess.lower()

    if game.check_game_word():
        game.change_hidden_letter()
        game.remove_letter_guess()

        if game.hidden_game_word.lower() == game.game_word:
            game_won(game.game_word, game.lives, game.category, game.hidden_game_word, game.alphabet)
        else:
            game_title()
            play_game(game.game_word, game.hidden_game_word, game.lives, game.category)
    else: ## now breaking here
        game.remove_life()
        game.remove_letter_guess()

        if game.lives > 0:
            game_title()
            print(f"The letter '{game.letter_guess}' is not in the answer. You have {game.lives} lives remaining.\n")
            play_game(game.game_word, game.hidden_game_word, game.lives, game.category)
        else:
            game_title()

            game_word = display_game_word(game.game_word)
            print(f"The letter '{game.letter_guess}' is not in the answer. You have 0 lives remaining. The answer which you was trying to guess was {game_word}.\n")

            print(f"{game.category}\n")
            print(f"{game.hidden_game_word}\n")
            print(f"Remaining letters: {display_alphabet.upper()}\n")

            reset_game()


def validate_letter(letter_guess, remaining_letters):
    """
    Inside the try checks whether an string has been entered and
    whether it is within the list of remaining letters to guess.
    Raises ValueError as appropriate.
    """

    try:
        str(letter_guess)

        if letter_guess not in remaining_letters:
            raise ValueError(
                f"You entered '{letter_guess}'"
            )

    except ValueError as e:
        game_title()
        print(f"ValueError: {e}. Please enter one of the remaining letters (shown below).\n")
        return False

    return True


def main():
    """
    Run all program functions
    """
    game_title()
    lives = select_difficluty()
    column, category = select_category()
    game_word = retrieve_word(column)
    hidden_game_word = hide_game_word(game_word)
    play_game(game_word, hidden_game_word, lives, category)


main()

