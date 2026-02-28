
# 1. Define the function
def filter_even_numbers(number_list):
    evens = []
    for num in number_list:
        if num % 2 == 0:
            evens.append(num)
    return evens

# 2. Prepare some data
my_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# 3. Call the function and store the result
result = filter_even_numbers(my_numbers)

# 4. Print the result
print(f"Original list: {my_numbers}")
print(f"Even numbers only: {result}")
