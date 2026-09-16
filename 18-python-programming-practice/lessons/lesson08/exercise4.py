string = "Since Boris Johnson announced he would leave office in July, the outlook for growth has weakened. Annual inflation is running above 10% as food and fuel prices leap. Frustration over the rising cost of living has compelled hundreds of thousands of workers who staff ports, trains and mailrooms to go on strike. The British pound just logged its worst month since the aftermath of the 2016 Brexit referendum, hitting its lowest level against the US dollar in more than two years."

my_list = list(string)
print(my_list)

dictionary = {}

for char in my_list:
    if char not in dictionary:
        dictionary[char] = 1
    else:
        dictionary[char] += 1

print(dictionary)

max_value = max(list(dictionary.values()))
print(max_value)
print(dictionary)

for key, value in dictionary.items():

    if value == max_value:
        if key == " ":
            print("blank")
        else:
            print(key)