f = open("filenames.list","r")
while True:
  contents = f.readline().strip()
  print(contents)
  
  if contents == "":
    break
