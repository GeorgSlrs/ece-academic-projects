import os,time
var = "List organizer"
print(f"{var:^10}")
print("="*15)
time.sleep(3)
os.system("clear")
toDoList = []

def remove():
  time.sleep(1)
  os.system("clear")
  find = input("Name of todo to remove > ")
  for row in toDoList:
    if find in row:
      toDoList.remove(row)


def view():
  time.sleep(1)
  os.system("clear")
  options = input("1: All\n2: By Priority\n> ")
  if options=="1":
    for row in toDoList:
      for item in row:
        print(item, end=" | ")
      print()
    print()
  else:
    priority = input("What priority? > ").capitalize()
    for row in toDoList:
      if priority in row:
        for item in row:
          print(item, end=" | ")
        print()
    print()
  time.sleep(1)

def add():
  time.sleep(1)
  os.system("clear")
  name = input("Name > ")
  date = input("Due Date > ")
  priority = input("Priority > ").capitalize()
  row = [name, date, priority]
  toDoList.append(row)
  print("Added")

def move():
  time.sleep(1)
  os.system("clear")
  find = input("Name of todo to edit > ")
  found = False
  for row in toDoList:
    if find in row:
      found = True
  if not found:
    print("Couldn't find that")
    return
  for row in toDoList:
    if find in row:
      toDoList.remove(row)
  name = input("Name > ")
  date = input("Due Date > ")
  priority = input("Priority > ").capitalize()
  row = [name, date, priority]
  toDoList.append(row)
  print("Added")


while True:
  time.sleep(1.5)
  os.system("clear")
  print("Menu")
  print()
  print("1 - Add    (Type a)")
  print("2 - View   (Type v)")
  print("3 - Move   (Type m)")
  print("4 - Remove (Type r)")
  print()
  userOption = input("What would you like to do? ").lower()
  
  if userOption == "v":
    view()
  elif userOption == "a":
    add()
  elif userOption == "m":
    move()
  elif userOption == "r":
    remove()
  else:
    print("That is not a viable option. Please choose again!")
    continue
