import os
import time
toDoList = []

def printList():
  i = 0
  for item in toDoList:
    print(f"Activity {i}: {item}")
    i += 1
while True:
  toDo = input("What to do you want to do? (A for adding an activity, R for removing an activity): ")
  if toDo == "R":
    item = input("Type the name of the item you want to remove: ")
    if item in toDoList:
      toDoList.remove(item)
      continue
  elif toDo == "A":
    item = input("Which activity you want to add in the list? ")
    toDoList.append(item)
  else:
    break
  time.sleep(1)
  os.system("clear")

print()
print("So your to-do list is as follows")
printList()
