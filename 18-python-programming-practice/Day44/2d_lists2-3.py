def prettyPrint():
  print() 
  for row in listOfShame: 
    for item in row: 
      # item refers to each item in the column for that row
     print(f"{item:^10}", end=" | ") 
      # :^10 means 10 characters as the space with the data in the center. The end character has been changed to space vertical line space to make it look more like a table.
      
    print() 
    
  print()

listOfShame = [] 
while True: 
  name = input("What is your name? ")
  age = input("What is your age? ")
  pref = input("What is your computer platform? ")
  
  row = [name, age, pref] 
  listOfShame.append(row) 
  exit = input("Exit? y/n") 
  if (exit.strip().lower()[0] == "y"):
    break 
prettyPrint() 
# Call the prettyPrint subroutine instead of printing the list directly.
