import os, time
print('\033[?25l', end="") #clears the cursor
for i in range(1, 101):
  print(i)
  time.sleep(0.2)
  os.system("clear")

print('\033[?25l', end="") #the cursor then reappears
