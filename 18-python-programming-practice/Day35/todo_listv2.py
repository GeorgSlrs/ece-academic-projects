import os
import time
toDoList = []



def printList():
  i = 0
  for item in toDoList:
    print(f"Activity {i}: {item}")
    i += 1



while True:
  j = 0
  print("*****************************")
  print("Menu of to-do list".center(30))
  print("*****************************")
  print("=============================")
  print("1-View")
  print("2-Add")
  print("3-Remove")
  print("4-Remove all")
  print("5-Edit")
  print("==============================")
  print()
  toDo = input("What to do you want to do? (1 for viewing the list, 2 for adding an activity, 3 for removing an activity, 4 to erase the whole list): ")
  print()
  if toDo == "1":
   printList()
  elif toDo == "2":
    item = input("Which activity you want to add in the list? ")
    if item in toDoList:
      print("The activity you typed already exists in the to-do list.")
    else:
      toDoList.append(item)
  elif toDo == "3":
    item = input("Type the name of the activity you want to remove.")
    if item in toDoList:
      toDoList.remove(item)
  elif toDo == "4":
     item = input("Are you sure you want to erase the whole list? ")
     if (item == "Yes" or item == "yes"):
      toDoList = []
     else:
      print("So you chose not to erase the whole to-do list.")
      continue
  elif toDo == "5":
    item = input("Type the item you want to be edited.")
    new_item = input("Type the new item: ")
    if item in toDoList:
      for i in range(0, len(toDoList)):
        if toDoList[i] == item:
          toDoList[i] == new_item
    else:
      print("Element was not found in the toDoList.")
      continue
  time.sleep(1)
  os.system("clear")



print()
print("So your to-do list is as follows")
printList()
