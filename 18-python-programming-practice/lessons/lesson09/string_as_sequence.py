string = "Sample String"
print((string + " ") * 3)
print(string[1])
print(string[1:4] + string[-4:-1])
print(len(string))
print(max("sample"))
print(min("String"))
print(string.index("am"))
print(string.count("S"))
# str[2] = "c" not working

new_str = string[:2] + "c" + string[3:]
print(new_str)