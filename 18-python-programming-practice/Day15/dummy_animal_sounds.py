exit = 1
while (exit != 0):
  animal = input("Which animal sound do you want to hear?: ")
  if (animal == "Cow"):
    print("Moo")
  elif (animal == "Dog"):
    print("Woof")
  elif (animal == "Cat"):
    print("Meow")
  elif (animal == "Fish"):
    print("...")
  elif (animal == "Donkey"):
    print("Eeeeoh")
  elif (animal == "Monkey"):
    print("uuuuuuuuu")
  else:
    print("The given animal does not exist in my very small database")
  exit = int(input("Do you want to exit the program? (0 for yes)"))
