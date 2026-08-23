import random
def rollDice(sides):
  rolledDice = random.randint(1, sides + 1)
  return rolledDice

  
def roll2Dice():
  doubleDice = rollDice(6) * rollDice(8)
  return doubleDice
  

health = roll2Dice()
name = input("Name your character: ")
print()
print("\033[40m","health: ",health,"name: ", name)
