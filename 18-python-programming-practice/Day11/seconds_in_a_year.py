year = input("Is this a leap year?(Y/N): ")
if (year == "Y"):
  days = 366
else:
  days = 365
total_seconds_in_a_year = days*24*60*60
print("There are",total_seconds_in_a_year,"seconds only")
