import glob
import operator

"""
A simple script to count the lines of code in each file,
and in the project as a whole.
"""

count = 0
d = {}

for filename in glob.iglob("src/" + "**/*.py", recursive=True):
    with open(filename, "r") as f:
        c = len(f.readlines())

    d[filename] = c
    count += c

s = sorted(d.items(), key=operator.itemgetter(1), reverse=True)
for filename, c in s:
    print(f"{c} lines in {filename}.")

print(f"\nTotal number of .py files: {len(s)}")
print(f"Total line count: {count}")
print(f"Total line count excluding licence headers: {count - len(s)*15}")
