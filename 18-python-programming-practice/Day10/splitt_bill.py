totalBill = float(input("Enter the total bill: "))
percentangeTip = float(input("Enter the percentage of the tip: "))

totalBill = totalBill + (percentangeTip*totalBill)

people = int(input("How many people are splitting the bill?: "))

perPersonBill = totalBill / people
perPersonBill = round(perPersonBill, 2)

print("You each owe",perPersonBill,"$.")
