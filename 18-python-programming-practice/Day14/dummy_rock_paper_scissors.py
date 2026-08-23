from getpass import getpass as input

print("Rock-Paper-Scissors game")
print()
print("===================================")
inputPlayer1 = input("Player 1 is playing. Type R for rock S for Scissors and P for paper: ")
if (inputPlayer1 != "R" and inputPlayer1 != "C" and inputPlayer1 and "P"):
  print("Wrong input. The game has ended.Player2 wins")
else:
  inputPlayer2 = input("Player 2 is playing. Type R for rock S for Scissors and P for paper: ")
  print()
  print("The game has started.")
  if(inputPlayer1 == "R" and inputPlayer2 == "S"):
    print("Player1 wins.")
  elif(inputPlayer1 == "S" and inputPlayer2 == "P"):
    print("Player 1 wins.")
  elif(inputPlayer1 == "P" and inputPlayer2 == "R"):
    print("Player1 wins.")
  elif(inputPlayer1 == inputPlayer2):
    print("It is a tie")
  else:
    print("Player2 wins.")
print("=================================")
