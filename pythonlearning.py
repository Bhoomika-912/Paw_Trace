import random

# Define hangman stages
HANGMAN = [
    '''
     -----
     |   |
         |
         |
         |
         |
    ''',
    '''
     -----
     |   |
     O   |
         |
         |
         |
    ''',
    '''
     -----
     |   |
     O   |
     |   |
         |
         |
    ''',
    '''
     -----
     |   |
     O   |
    /|   |
         |
         |
    ''',
    '''
     -----
     |   |
     O   |
    /|\\  |
         |
         |
    ''',
    '''
     -----
     |   |
     O   |
    /|\\  |
    /    |
         |
    ''',
    '''
     -----
     |   |
     O   |
    /|\\  |
    / \\  |
    '''
]

# Categories with words
categories = {
    "movies": ["inception", "avatar", "matrix", "gladiator", "titanic", "godfather", "joker", "starwars", "shawshank", "interstellar"],
    "sports": ["football", "tennis", "basketball", "cricket", "baseball", "hockey", "volleyball", "rugby", "golf", "boxing"],
    "programming": ["python", "developer", "backend", "firewall", "javascript", "algorithm", "database", "frontend", "html", "typescript"]
}

# Function to choose category
def choose_category():
    while True:
        print("Choose a category:")
        for cat in categories:
            print("-", cat)

        choice = input("Your category: ").lower()

        if choice in categories:
            return choice
        else:
            print("Invalid category. Please choose one of the listed options.\n")

# Function to display current game status
def display_status(display_word, wrong_guesses, num):
    print("Word: " + " ".join(display_word))  # Display word with spaces
    print(f"Wrong guesses: {', '.join(wrong_guesses)}")  # Show wrong guesses so far
    print(HANGMAN[num])  # Show current hangman step

# Function to check if input is valid
def get_valid_guess():
    while True:
        guess = input("Guess a letter: ").lower()
        if len(guess) == 1 and guess.isalpha():
            return guess
        else:
            print("Invalid input. Please enter a single letter.")

# Main function to start the game
def play_game():
    # Choose category and word
    category = choose_category()
    secret_word = random.choice(categories[category])

    # Initialize game variables
    display_word = ["_"] * len(secret_word)
    wrong_guesses = []
    num = 0
    game_over = False

    print(f"\nYou've chosen {category} category!\n")
    print("\nYou have 5 guesses\n")

    # Main game loop
    while not game_over:
        display_status(display_word, wrong_guesses, num)
        guess = get_valid_guess()

        # Check if guess is correct
        if guess in secret_word:
            for position in range(len(secret_word)):
                if secret_word[position] == guess:
                    display_word[position] = guess
        else:
            wrong_guesses.append(guess)
            num += 1
            guesses_left = 5 - num
            print(f"You have {guesses_left} guesses left")

        # Check for game over conditions
        if num >= 5:
            display_status(display_word, wrong_guesses, num)
            print("Better luck next time ^^")
            print(f"The word was: {secret_word}")
            game_over = True
        elif "_" not in display_word:
            display_status(display_word, wrong_guesses, num)
            print("Congratz, you won!")
            game_over = True

# Start the game
play_game()
