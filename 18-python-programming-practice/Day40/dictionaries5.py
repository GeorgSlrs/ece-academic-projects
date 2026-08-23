print("===================")
print("  Contanct Card")
print("===================")

name = input("Please type in your name: ")
dateOfBirth = input("Please type in your date of birth: ")
e_mail = input("Please type in your e-mail: ")
telephone = input("Please type in your telephone number: ")
physical_address = input("Please type in ypur physical address: ")

personal_info = {"name" : name, "date of birth" : dateOfBirth, "email" : e_mail, "telephone_number" : telephone, "physical address" : physical_address}

for key in personal_info.keys():
  print(key, personal_info[key])
  print()
