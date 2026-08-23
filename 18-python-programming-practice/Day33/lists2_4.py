myAgenda = []

def printList():
  print() 
  for item in myAgenda:
    print(item)
  print() 

while True:
  menu = input("Add or Remove?: ")
  if menu == "add":
    item = input("What's next on the Agenda?: ")
    item.append(myAgenda)
  elif menu == "remove":
    item = ("What do you want to remove?: ")
    if item in myAgenda:
      item.remove(myAgenda)
    else:
      print(f"{item} was not in the list")
  printList()
