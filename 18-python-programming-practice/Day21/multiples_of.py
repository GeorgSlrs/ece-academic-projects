score = 0
print("Multiplication game")
multiples = int(input("Multiples of?: "))
for i in range(0,11,1):
  print(i ,"x" ,multiples)
  res = int(input("->"))
  correct = i * multiples
  if (res == correct):
    print("Nice! The answer you gave was correct!")
    score += 1
  else:
    print("Sorry, but the answer you gave is wrong.The correct answer is", i * correct)
print("The game has ended.")
if (score == 11):
  print("Perefect")
else:
  print("So the game is over. You got",score,"/10.")
