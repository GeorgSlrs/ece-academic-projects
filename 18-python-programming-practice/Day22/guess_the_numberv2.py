import random

print("Guess the number game")
print("=====================")
hiddenNumber = random.randint(0,1000000)
numberOfTries = 0
while True:
  guessedNumber = int(input("Please enter an integer between 0 and 1000000: "))
  if guessedNumber < 0:
    exit()
  else:
    if guessedNumber > hiddenNumber:
        print("Too high.")
        numberOfTries += 1
        continue
    elif guessedNumber < hiddenNumber:
        print("Too low.")
        numberOfTries += 1
        continue
    else:
      print("If you typed a number, then you typed the correct one.In other occasion the below result is wrong.")
      print("Bullseye!")
      numberOfTries += 1
      break
print("So it took you",numberOfTries,"to guess the number.Nice!")
