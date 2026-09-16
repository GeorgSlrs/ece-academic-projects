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

max_rounds = 10
for round in range(1, max_rounds+1):
    print(f"ROUND {round}")

    while True:
        letter = input("Give a letter: ").lower()
        if len(letter)!= 1:
            print("Error. Please give ONE letter!!")
        elif not letter.isalpha():
            print("Error. Please write letters!!")

        elif letter in guessed_letters:
            print("You have already typed this letter!!")
        else:
            break

        guessed_letters.append(letter)
        print(f"Letter {letter} exists {hidden_word.count(letter)} in hidden word")
        found = True
        for char in hidden_word:
            if char in guessed_letters:
                print(char, end = "")
            else:
                print("_", end = "")
                found = False

        print("")
        if found:
            print("Success! You've found it!")
            break

else:
    print("Failure! Maximum rounds reached!")
    print("The hidden word was " + hidden_word)


