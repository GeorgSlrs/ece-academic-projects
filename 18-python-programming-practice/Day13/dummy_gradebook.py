courseTestName = input("Please enter the name of the test's course: ")
maxScore = float(input("Please enter the maximum possible score in the test: "))
userScore = float(input("Please enter how much you got in the test-the score: "))
percentageOfScore = (userScore / maxScore) * 100
typeOfScore = "none"
if percentageOfScore >=90:
    typeOfScore = "A+"
elif percentageOfScore >= 80:
    typeOfScore = "A-"
elif percentageOfScore >= 70:
    typeOfScore = "B"
elif percentageOfScore >= 60:
    typeOfScore = "C"
elif percentageOfScore >= 50:
    typeOfScore = "D"
else:
    typeOfScore = "C"

percentageOfScore = round(percentageOfScore,2)
print("So you got", percentageOfScore,"which is a", typeOfScore)
print()
print("\033[1;32m Nice!  \n")
