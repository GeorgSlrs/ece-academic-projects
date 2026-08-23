names = []

def printList():
  print()
  for name in names:
    print(name)
  print()

while True:
  first_name = input("Type in your first name: ").strip().capitalize()
  last_name = input("Type in your last name: ").strip().capitalize()
  name = f"{first_name} {last_name}"
  if name not in names:
    names.append(name)
