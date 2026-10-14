# def add(symbol : str, address : int):
#   addr = bin(address)[2:]
#   x = "0" * (15 - len(addr)) + addr
#   print(x)
# add("fdsa", 40)

# def test(file):
#   for line in file.readlines():
#     print(line, end="")
  

# file = open("test.asm", "r")

# test(file)
  
# for line in file.readlines():
#   print(line, end="")

s = ""
# print(len(s.strip()))
l = ["asd", "fady"]
print(l[1][0:2])

d = {1 : 3, 5 : 6}
d1 = {11 : 33, 7 : 4}


[
{'num': 0, 'inst_num': 0, 'inst_type': 'A', 'label': '5'},
{'num': 1, 'inst_num': 1, 'inst_type': 'C', 'dest': 'D', 'comp': 'A'},
{'num': 2, 'inst_num': 2, 'inst_type': 'A', 'label': 'R1'},
{'num': 4, 'inst_num': 3, 'inst_type': 'C', 'dest': 'M', 'comp': 'D'},
{'num': 6, 'inst_num': 4, 'inst_type': 'C', 'dest': 'D', 'comp': 'A+1', 'jump': 'JLT'},
{'num': 8, 'inst_num': 5, 'inst_type': 'C', 'dest': 'A', 'comp': ' A+1'},
{'num': 13, 'inst_num': 6, 'inst_type': 'C', 'comp': 'D&A'}
]
[
{'num': 0, 'inst_num': 0, 'inst_type': 'A', 'label': '5'},
{'num': 1, 'inst_num': 1, 'inst_type': 'C', 'dest': 'D', 'comp': 'A', 'jump': 'null'},
{'num': 2, 'inst_num': 2, 'inst_type': 'A', 'label': 'R1'},
{'num': 4, 'inst_num': 3, 'inst_type': 'C', 'dest': 'M', 'comp': 'D', 'jump': 'null'},
{'num': 6, 'inst_num': 4, 'inst_type': 'C', 'dest': 'D', 'comp': 'A+1', 'jump': 'JLT'},
{'num': 8, 'inst_num': 5, 'inst_type': 'C', 'dest': 'A', 'comp': ' A+1', 'jump': 'null'},
{'num': 13, 'inst_num': 6, 'inst_type': 'C', 'comp': 'D&A', 'jump': 'null', 'dest': 'null'}
]
{'fady': '000000000000101', 
'test': '000000000000110'}
# for i, c in enumerate("fady"):
#   print(i)
#   print(c)
  
# s = "     fady      \n"
# t = s.strip(" \n")
# print(t)
# print(len(t))
# s.strip()

# file = open("new.hack", "w")
# file.writelines(["fady\n", "adel\n"])
s = "fady"
print(s[-2:])