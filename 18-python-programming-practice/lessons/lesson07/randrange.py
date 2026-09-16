from random import randrange

words = [
    "player",
    "warning",
    "imagination",
    "percentage",
    "reading",
    "understanding",
    "estate",
    "highway",
    "response",
    "clothes",
    "context",
    "philosophy",
    "government",
    "virus",
    "location"
]

hidden_word = words[randrange(len(words))]
print(hidden_word)
guessed_letters = []
while True:
    letter = input("Give a letter: ")

    guessed_letters.append(letter)
    print(f"Letter {letter} exists {hidden_word.count(letter)} in hidden word")
    found = True
    for char in hidden_word:
        if char in guessed_letters:
            print(char, end = "")
        else:
            print("_", end = "")
            found = False

    if found:
        print("Success! You've found it!")
        break




