from sys import argv

def main():
  # i can use   argv[1].endswith(".vm") 😄
  if (len(argv) != 2) or argv[1][-3:] != ".vm":
    print("Usage: python VMTranslator.py FILENAME.vm")
    exit(1)
  try:
    file = open(argv[1], "r")
  except:
    print(f"Could not open {argv[1]}")
    exit(1)
  
  data = file.readlines()
  file.close()
  result = VMTranslator().translate(data)
  if result == 0:
    return 0
  else:
    print(result)
    exit(2)


class VMTranslator:
  def __init__(self):
    self.parser = Parser()
    self.coder = Coder()
  
  def translate(self, data):
    parsed = self.parser.parse(data)
    if type(parsed) == int:
      return f"Error in line {parsed}"
    self.coder.write_code(parsed, argv[1][0:-3])
    return 0

class Parser:
  def __init__(self):
    self.arithmetic = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]
    # remember to add ["constant"] with push command
    self.segments = ["local", "argument", "this", "that", "static", "pointer", "temp"]

  def parse(self, data):
    parsed_commands = []
    for i, line in enumerate(data):
      line = line.strip()
      length = len(line)
      if length == 0 or line[0:2] == "//":
        continue
      else:
        command = self.parse_line(line)
        if len(command) > 0 and self.isValid(command):
          parsed_commands.append(command)
        else:
          return i
        
    return parsed_commands
  
  def parse_line(self, line):
    command = dict()
    command["line"] = line
    line = line.split()
    if line[0] in self.arithmetic:
      command["type"] = "C_ARITHMETIC"
      command["command"] = line[0]
    elif len(line) == 3:
      if line[0] == "push":
        command["type"] = "C_PUSH"
      elif line[0] == "pop":
        command["type"] = "C_POP"
      # maybe gonna add more in VMTranslator part 2
      command["segment"] = line[1]
      command["i"] = line[2]
    return command

  def isValid(self, command):
    # there is no checking for i being 0 or 1 while segment is pointer
    if command["type"] == "C_ARITHMETIC":
      return command["command"] in self.arithmetic
    elif command["type"] == "C_PUSH":
      return command["segment"] in self.segments + ["constant"] and self.__is_realNumber(command["i"])
    elif command["type"] == "C_POP":
      return command["segment"] in self.segments and command["i"].isdecimal()
    # maybe gonna add more in VMTranslator part 2
    else:
      return False
    
  def __is_realNumber(self, s):
    if len(s) == 0:
      return False
    elif s[0] == "-":
      return s[1:].isdecimal()
    else:
      return s.isdecimal()

class Coder:
  def write_code(self, lines, file_name):
    file = open(file_name + ".asm", "w")
    file_name = file_name.split('\\')[-1][0:-3]
    comp_count = 0
    for line in lines:
      file.write(f"// {line["line"]}\n")
      if line["type"] == "C_ARITHMETIC":
        file.write(self.arithmetic(line["command"], comp_count))
        if line["command"] in ["eq", "gt", "lt"]:
          comp_count += 1 
      elif line["type"] == "C_PUSH":
        file.write(self.push(line["segment"], line["i"], file_name))
      elif line["type"] == "C_POP":
        file.write(self.pop(line["segment"], line["i"], file_name))
      else:
        # for debugging
        file.write(f"// error")
    file.close()
    return
  
  
  def push(self, segment, i, file_name):
    # beware temp
    if segment in ["local", "this", "that", "argument", "temp"]:
      addr = "5" if segment == "temp" else self.converter(segment)
      MorA = "A" if segment == "temp" else "M"
      return f"@{i}\nD=A\n@{addr}\nA=D+{MorA}\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n"
    elif segment in ["constant", "pointer", "static"]:
      # sign for negative constants
      sign = "-" if int(i) < 0 else ""
      i = i[1:] if int(i) < 0 else i
      MorA = "A" if segment == "constant" else "M"
      addr = i if segment == "constant" else f"{file_name}.{i}" if segment == "static" else self.converter(i)
      return f"@{addr}\nD={sign}{MorA}\n@SP\nAM=M+1\nA=A-1\nM=D\n"
    else:
      return ""
  
  def pop(self, segment, i, file_name):
    # beware temp
    if segment in ["local", "this", "that", "argument", "temp"]:
      addr = "5" if segment == "temp" else self.converter(segment)
      MorA = "A" if segment == "temp" else "M"
      return f"@{i}\nD=A\n@{addr}\nD=D+{MorA}\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n"
    elif segment in ["pointer", "static"]:
      addr = f"{file_name}.{i}" if segment == "static" else self.converter(i)
      return f"@SP\nAM=M-1\nD=M\n@{addr}\nM=D\n"
    else:
      return ""
  
  def arithmetic(self, command, comp_count):
    sign = self.converter(command)
    if command in ["add", "sub", "and", "or"]:
      operation = f"M=M{sign}D" if command == "sub" else f"M=D{sign}M"
      return f"@SP\nAM=M-1\nD=M\nA=A-1\n{operation}\n"
    elif command in ["neg", "not"]:
      return f"@SP\nA=M-1\nM={sign}M\n"
    elif command in ["eq", "gt", "lt"]:
      label = "END_" + sign + str(comp_count)
      return f"@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\nM=-1\n@{label}\nD;{sign}\n@SP\nA=M-1\nM=0\n({label})\n"
    else:
      return ""
  
  
  def converter(self, command):
    return {"add" : "+",
            "sub" : "-",
            "neg" : "-",
            "and" : "&",
            "or"  : "|",
            "not" : "!",
            "eq"  : "JEQ",
            "gt"  : "JGT",
            "lt"  : "JLT",
            
            "0"   : "THIS",
            "1"   : "THAT",
            
            "this"     : "THIS",
            "that"     : "THAT",
            "local"    : "LCL",
            "argument" : "ARG",}[command]


if __name__ == "__main__":
  main()