import random
import time
import os

def nameCharacter():
  name = input("Type your character's nickname: ")
  return name

def typeCharacter():
  typeCharacter = input("What is your character's type: ")
  return typeCharacter

def rollDice(sides):
  return random.randint(1, sides)

def setHealth():
  return (rollDice(6) * rollDice(12) / 2) + 10

def setStrength():
  return (rollDice(6) * rollDice(12) / 2) + 10

while True:
  print("⚔️ CHARACTER BUILDER ⚔️")
  name = nameCharacter()
  type = typeCharacter()
  strength = setStrength()
  health = setHealth()
  print("================================")
  print("nickname: ", "type: ", type)
  print("Health: ", health, "Strength: ", strength)
  print("================================")
  continue_game = input("Continue? (Type Y for yes): ")
  if (continue_game != "Y"):
    break
  else:
    time.sleep(2)
    os.system("clear") #   Clears what we wrote above
    continue #not necessary
