name = input("Tell me, what is your name?: ")
age = input("Tell me your age, please: ")
day = input("Which day do we have today?: ")
print("Hello",name,"It is a nice",day,"no?")
print()
print("Nice,you are"+" " + age + " years old.")
interest = input("Tell me which is your interest?: ")
if (interest == "nothing" or interest == "Nothing" or interest == "none" or interest == "None"):
  print("I am sorry to hear that")
mood = input("Tell me, on a scale from 0 to 10 what is your mood today? ")
if (mood == "6" or mood == "7" or mood == "8" or mood == "9" or mood == "10"):
  print("Nice, although you should be happier")
  if (mood == "9" or mood == "10"):
    print("Niceeeeeeee")
    print()
    if(mood == "10"):
      print("Bruh nobody can be that happy. Take time to sit down and think")

  else:
    print("It is ok to feel bad but trust me, things are going to get way better")
  print()
  print("Continue pursuading",interest,"if that is what it fullfills you")
print("Bye")
