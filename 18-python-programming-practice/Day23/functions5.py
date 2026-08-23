def loginSystem():
  while True:
    username = input("Type your username: ")
    password = input("Type your password: ")
    if (username == "oof" and password == "1234"):
      print("Welcome oof!")
      break
    else:
      print("Wrong input")
      continue

print("Dummy login system")
loginSystem()
