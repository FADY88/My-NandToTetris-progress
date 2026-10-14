from sys import argv

def main():
  if (len(argv) != 2) or argv[1][-4:] != ".asm":
    print("Usage: python hackAssembler.py FILENAME.asm")
    exit(1)
  try:
    file = open(argv[1], "r")
  except:
    print(f"Could not open {argv[1]}")
    exit(1)
  
  data = file.readlines()
  file.close()
  result = HackAssembler(data).assemble()
  if result == 0:
    return 0
  else:
    print(f"Error: {result}")
    exit(2)

class HackAssembler:
  def __init__(self, data):
    """ initialize the process of assembly the data to machine code
        if successful return 0
        otherwise return error message
    """
    self.data = data
    self.symbol = Symbols()
    return
  
  
  def assemble(self):
    """ start the process of assembly the file to machine code
        if successful return 0
        otherwise return error message
    """
    parsed_instructions = Parser(self.data, self.symbol).parse()
    # print("from assemble function")
    # print(parsed_instructions[0])
    # print()
    # print(self.symbol.variables)
    
    # decode the parsed code
    code = Code(self.symbol)
    result = code.decode(parsed_instructions)
    # return error message in a str
    if type(result) == str:
      return result
    # return decoded list[str]
    else:
      code.output(result, argv[1])
      return 0

class Parser:
  def __init__(self, data, tables):
    """ gits ready to parse data
    Args:
        data ( list[str] ): source code
    """
    self.data = data
    self.tables = tables
    return
  
  def parse(self):
    """ parse data in file and return list of dictionaries """
    return self.secondPass(self.firstPass(self.data))
  

  def firstPass(self, data : list[str]):
    """ Reads the program and adds the found labels to the variable table
        replace empty lines and comments with empty str """
    inst_num = 0
    tmp_vars = []
    for i, line in enumerate(data):
      line = line.strip()
      length = len(line)
      if length == 0:
        data[i] = ""
      elif line[0] == "(" and line[length - 1] == ")":
        tmp_vars.append(line[1:length - 1].strip())
        data[i] = ""
      elif line[0:2] == "//":
        data[i] = ""
      else:
        while tmp_vars:
          self.tables.add_label(tmp_vars.pop(), inst_num)

        inst_num += 1
        data[i] = line
      
    return data
  
  def secondPass(self, data : list[str]):
    """ Lines[str] -> instruction[dict] 
        dict -> {"num" : int, "inst_num" : int, "inst_type" : str, (x)}
        int_type   x                                          action
            # "L"   "label" : str                               store in variables
            "A"   "value" : str or int                        store binary or search for variable
            "C"   "dest" : str, "comp" : str, "jump" : str"""
    instructions = []
    inst_num = 0
    for i, line in enumerate(data):
      if len(line) == 0:
        continue
      else:
        inst = {"num" : i, "inst_num" : inst_num}
        if line[0] == "@":
          inst["inst_type"] = "A"
          inst["label"] = line[1:].strip()
          self.tables.add_var(inst["label"])
          instructions.append(inst)
        else:
          inst["inst_type"] = "C"
          instructions.append(self.__parse_C(line, inst))
        inst_num += 1
    
    return instructions
  
  def __parse_C(self, line, d):
    part = ""
    for i, c in enumerate(line):
      if c == "=":
        d["dest"] = part.strip()
        part = ""
      elif c == ";":
        d["comp"] = part.strip()
        d["jump"] = line[i+1:].strip()
        break
      elif i == len(line) - 1:
        part += c
        d["comp"] = part.strip()
      else:
        part += c
    keys = d.keys()
    if "jump" not in keys:
      d["jump"] = "null"
    if "dest" not in keys:
      d["dest"] = "null"
    return d


# will implement next
class Code:
  def __init__(self, tables):
    self.tables = tables
  
  def decode(self, instructions):
    """ decode instructions
        return list[str]"""
    decoded_list = []
    for inst in instructions:
      if inst["inst_type"] == "A":
        decoded_list.append(self.decode_A(inst))
      elif inst["inst_type"] == "C":
        code = self.decode_C(inst)
        if "mistake" == code.split()[0]:
          return code
        decoded_list.append(code)
      else:
        return f"Fatal error in line {inst["num"]}"
    length = len(decoded_list)
    decoded_list[length - 1] = decoded_list[length - 1].strip()
    return decoded_list
  
  def decode_A(self, inst):
    return "0" + self.tables.variables[inst["label"]] + "\n"

  def decode_C(self, inst):
    # {'num': 4, 'inst_num': 3, 'inst_type': 'C', 'dest': 'M', 'comp': 'D', 'jump': 'null'}
    # without checking for the correctness of "comp", "dest" and "jump"
    if self.tables.is_comp(inst["comp"]) and self.tables.is_dest(inst["dest"]) and self.tables.is_jump(inst["jump"]):
      return "111" + self.tables.get_comp(inst["comp"]) + self.tables.get_dest(inst["dest"]) + self.tables.get_jump(inst["jump"]) + "\n"
    else:
      return f"mistake in line {inst["num"]}\n{inst}"

  def output(self, instructions, file_name):
    """ write instructions into the file"""
    file = open(file_name[:-4] + ".hack", "w")
    file.writelines(instructions)
    return

class Symbols:
  def __init__(self):
    """initialize constant tables"""
    self.variable = 16
    
    self.comp = { "0"   : "0101010",
                  "1"   : "0111111",
                  "-1"   : "0111010",
                  "D"   : "0001100",
                  "A"   : "0110000", "M"   : "1110000",
                  "!D"  : "0001101",
                  "!A"  : "0110001", "!M"  : "1110001",
                  "-D"  : "0001111",
                  "-A"  : "0110011", "-M"  : "1110011",
                  "D+1" : "0011111",
                  "A+1" : "0110111", "M+1" : "1110111",
                  "D-1" : "0001110",
                  "A-1" : "0110010", "M-1" : "1110010",
                  "D+A" : "0000010", "D+M" : "1000010",
                  "D-A" : "0010011", "D-M" : "1010011",
                  "A-D" : "0000111", "M-D" : "1000111",
                  "D&A" : "0000000", "D&M" : "1000000",
                  "D|A" : "0010101", "D|M" : "1010101",}
    self.dest = { "null" : "000",
                  "M"    : "001",
                  "D"    : "010",
                  
                  "DM"   : "011",
                  "MD"   : "011",
                  
                  "A"    : "100",
                  
                  "AM"   : "101",
                  "MA"   : "101",
                  
                  "AD"   : "110",
                  "DA"   : "110",
                  
                  "ADM"  : "111",
                  "AMD"  : "111",
                  
                  "DMA"  : "111",
                  "DAM"  : "111",
                  
                  "MAD"  : "111",
                  "MDA"  : "111"}
    self.jump = { "null" : "000",
                  "JGT"  : "001",
                  "JEQ"  : "010",
                  "JGE"  : "011",
                  "JLT"  : "100",
                  "JNE"  : "101",
                  "JLE"  : "110",
                  "JMP"  : "111"}
    self.variables = {"R0"     : "000000000000000",
                      "R1"     : "000000000000001",
                      "R2"     : "000000000000010",
                      "R3"     : "000000000000011",
                      "R4"     : "000000000000100",
                      "R5"     : "000000000000101",
                      "R6"     : "000000000000110",
                      "R7"     : "000000000000111",
                      "R8"     : "000000000001000",
                      "R9"     : "000000000001001",
                      "R10"    : "000000000001010",
                      "R11"    : "000000000001011",
                      "R12"    : "000000000001100",
                      "R13"    : "000000000001101",
                      "R14"    : "000000000001110",
                      "R15"    : "000000000001111",
                      "SP"     : "000000000000000",
                      "LCL"    : "000000000000001",
                      "ARG"    : "000000000000010",
                      "THIS"   : "000000000000011",
                      "THAT"   : "000000000000100",
                      "SCREEN" : "100000000000000",
                      "KBD"    : "110000000000000",}
    return
  
  def add_label(self, symbol : str, address : int):
    """ adds a variable to variables table"""
    addr = bin(address)[2:]
    self.variables[symbol] = "0" * (15 - len(addr)) + addr
    return

  def add_var(self, symbol : str):
    """ adds a variable or a number to variables table"""
    if self.is_variable(symbol):
      return
    if symbol.isdecimal():
      address = int(symbol)
    else:
      address = self.variable
      self.variable += 1
    self.add_label(symbol, address)
    return
  
  def is_variable(self, symbol):
    """ searches for symbol in variables table """
    return symbol in self.variables.keys()
  
  def is_comp(self, symbol):
    return symbol in self.comp.keys()

  def is_dest(self, symbol):
    return symbol in self.dest.keys()

  def is_jump(self, symbol):
    return symbol in self.jump.keys()
  
  def get_comp(self, symbol):
    return self.comp[symbol]
  
  def get_dest(self, symbol):
    return self.dest[symbol]
  
  def get_jump(self, symbol):
    return self.jump[symbol]
  
  def get_variable(self, symbol):
    return self.variables[symbol]





if __name__ == "__main__":
  main()