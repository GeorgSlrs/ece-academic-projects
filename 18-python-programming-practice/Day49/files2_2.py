f = open("filenames.list", "r")
contents = f.read()
f.close()

contents = contents.split() #added split here

print(contents)
