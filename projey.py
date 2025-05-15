import sys

file = open(sys.argv[1], "r")
lines = file.readlines()
print("Lines in the file:")
for line in lines:
    print(line)