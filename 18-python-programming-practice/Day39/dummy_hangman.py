import random, os, time



tries = 6
listOfWords = ["apple", "orange", "grapes", "pear"]
letterPicked = []
allGuessed = True
print("======Hangman game======")
print()



chosen_word = random.choice(listOfWords) #picks a random word from the list



while tries > 0:
  time.sleep(1.5)
  os.system("clear")
  letter_user = input("Type in a letter: ").lower()
  

  if letter_user in chosen_word:
    print(f"The letter {letter_user} exists in the chosen   word") 
    if letter_user in letterPicked:
     print("Excuse me, but you have chosen a letter that you   already chose before")
    else:
      print("Nice! You have guessed a letter")
      letterPicked.append(letter_user)
  else:
    print(f"The letter {letter_user} does not exist")
    tries -= 1
    print(f"You have {tries} left")

  for letter in chosen_word:
   if letter in letterPicked:
      print(letter, end = "")
   else:
      print("_",end = "")
      allGuessed = False
  print()

  if allGuessed:
   print(f"You have won with {tries} left.")



print(f"You have ran out of tries. The original answer was {chosen_word}")
