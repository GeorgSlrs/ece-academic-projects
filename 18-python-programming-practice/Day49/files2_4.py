f = open("filenames.list","r")
while True:
  contents = f.readline().strip()
  
  if contents == "":
    break

  print(contents)
