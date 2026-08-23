tries = 1
print("Fill in the blans in my favourite song")
print()
print("Can you hear the ________ ?")
while True:
  guessedWord = input("Type the   correct word: ")
  if (guessedWord == "silence"):
    break
  else:
    print("Nope, that is not the correct word. Please try again")
    tries+=1
print("Nice! You guessed the correct word, which was",guessedWord,"and it only took you",tries,"tries.")
