print("Which is your Star Wars name?")
print("===============================")
name = input("Please type your name,surname,maiden name and city you were  born seperated by space: ").split()
first = name[0].strip()
last = name[1].strip()
maiden = name[2].strip()
city = name[3].strip()

name = f"{first[:3].title()}{last[:3].lower()} {maiden[:2].title()}{city[-3:].lower()}"

print("===============================")

print(f"Your Star Wars nickname is {name}")
