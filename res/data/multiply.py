"""
Script to take a file and repeat it many times, outputting a
much larger resultant data-set.
"""

file = "test.csv"
repeat = 100

with open(file, "r") as f:
    data = f.readlines()

output = []

for i in range(repeat):
    output.extend(data)  # Add items in data list to output list.

# Write data to file.
out_name = f"{file[:-4]}_extended.csv"
print(f"Writing to {out_name}")

with open(out_name, "w") as f:
    f.writelines(output)
