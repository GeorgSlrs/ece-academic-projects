import random
def rollDice(sides):
  rolledDice = random.randint(1, sides + 1)
  print("You rolled a", rolledDice)

sidesSelected = int(input("Please enter the number of sides of your dice: "))
rollDice(sidesSelected)

while True:
  play = input("Continue? ")
  if play == "yes" or play == "Yes":
    rollDice(sidesSelected)
  else:
    break
                          
