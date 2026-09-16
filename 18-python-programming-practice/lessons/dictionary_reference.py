# Sample dictionary
my_dict = {'apple': 3, 'banana': 5, 'cherry': 2}
print("Original dictionary:", my_dict)

# keys()
keys_view = my_dict.keys()
print("Keys view:", keys_view)

# values()
values_view = my_dict.values()
print("Values view:", values_view)

# items()
items_view = my_dict.items()
print("Items view:", items_view)

# get(): existing key vs. missing key with default
apple_count = my_dict.get('apple')
orange_count = my_dict.get('orange', 0)
print("Apple count:", apple_count)
print("Orange count (default 0):", orange_count)

# pop(): remove 'banana' and get its value
banana_count = my_dict.pop('banana')
print("Popped banana count:", banana_count)
print("After pop:", my_dict)

# update(): merge in new key/value pairs
result = my_dict.update({'date': 4, 'elderberry': 7})
print("Result of update():", result)
print("After update:", my_dict)

# clear(): remove all items
clear_result = my_dict.clear()
print("Result of clear():", clear_result)
print("After clear:", my_dict)
