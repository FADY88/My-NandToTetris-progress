from sys import argv
import os

def process_file(file_path):
  print(f'Processing file: {file_path}')
  # Add your file processing logic here
  try:
    file = open(file_path, "r")
  except:
    print(f"Could not open {file_path}")
    exit(1)
  
  data = file.readlines()
  file.close()
  return data


def process_directory(directory):
  # Hardcoded file extension
  extension = '.vm'
  data = []
  # Traverse the directory recursively
  for root, dirs, files in os.walk(directory):
    for file in files:
      if file.endswith(extension):
        file_path = os.path.join(root, file)
        # "-" will be "//" in final .asm file
        data.append(f"-{file_path}")
        data += process_file(file_path)
  return data


def main():
  # Check if the correct number of arguments is provided
  if len(argv) != 2:
    print("Usage: python VMTranslator.py [FILENAME.vm | DIRECTORY]")
    return
  
  # Get the path from command-line arguments
  path = argv[1]

  data = []
  # Check if the path is a file or a directory
  if os.path.isfile(path) and path.endswith('.vm'):
    # If it's a file, process it directly
    data = process_file(path)
  elif os.path.isdir(path):
    # If it's a directory, process all files with the specified extension
    data = process_directory(path)
  else:
    print('Error: The provided path is neither a .vm file nor a directory.')
    return

  result = VMTranslator().translate(data)
  # print(data)
  if result == 0:
    return 0
  else:
    print(result)
    return


class VMTranslator:
  def __init__(self):
    self.parser = Parser()
    self.coder = Coder()
  
  def translate(self, data):
    parsed = self.parser.parse(data)
    if type(parsed) == int:
      return f"Error in line {parsed}"
    if not argv[1].endswith(".vm"):
      argv[1] += "\\" + argv[1].split("\\")[-1]
    self.coder.write_code(parsed, argv[1].removesuffix(".vm"))
    return 0

class Parser:
  def __init__(self):
    self.arithmetic = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]
    # remember to add ["constant"] with push command
    self.segments = ["local", "argument", "this", "that", "static", "pointer", "temp"]
    
    self.control_flow = ["label", "goto", "if-goto"]
    self.fun_calling = ["function", "call", "return"]

  def parse(self, data):
    parsed_commands = []
    for i, line in enumerate(data):
      line = line.strip()
      length = len(line)
      if length == 0 or line[0:2] == "//":
        continue
      # VMTranslator part 2
      elif line[0] == "-":
        parsed_commands.append({"line" : line, "type" : "COMMENT", "comment" : line[1:]})
      # VMTranslator part 2
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
    line = line.split()[0:3]
    if line[0] in self.arithmetic:
      command["type"] = "C_ARITHMETIC"
      command["command"] = line[0]
    # VMTranslator part 2
    elif line[0] in self.control_flow:
      command["type"] = "CONTROL"
      command["command"] = line[0]
      command["label"] = line[1]
    elif line[0] in self.fun_calling:
      command["type"] = "FUN_CALLING"
      command["command"] = line[0]
      if line[0] in ["function", "call"]:
        command["function_name"] = line[1]
        # arg = "nArgs" if line[0] == "call" else "nVars"
        command["ArgsOrVars"] = line[2]
    # VMTranslator part 2
    elif len(line) == 3:
      if line[0] == "push":
        command["type"] = "C_PUSH"
      elif line[0] == "pop":
        command["type"] = "C_POP"
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
    # VMTranslator part 2
    elif command["type"] == "CONTROL":
      return command["command"] in self.control_flow and command["label"] != ""
    elif command["type"] == "FUN_CALLING": # edit
      return command["command"] == "return" or command["command"] in ["function", "call"] and self.__is_realNumber(command["ArgsOrVars"])
    # VMTranslator part 2
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
  def __init__(self):
    self.call_count = 0
    self.functionName = "Sys.init"
  
  def write_code(self, lines, file_name):
    file = open(file_name + ".asm", "w")
    file_name = file_name.split('\\')[-1].removesuffix(".vm")
    # comment following line when bootstrap code isn't needed
    file.write(self.Hack_init())
    comp_count = 0
    
    for line in lines:
      file.write(f"// {line['line']}\n")
      if line["type"] == "COMMENT": # VMTranslator part 2
        file.write(f"// Start of the file: {line['comment']}\n")
        file_name = line["comment"].split("\\")[-1].removesuffix(".vm")
      elif line["type"] == "C_ARITHMETIC":
        file.write(self.arithmetic(line["command"], comp_count))
        if line["command"] in ["eq", "gt", "lt"]:
          comp_count += 1 
      elif line["type"] == "C_PUSH":
        file.write(self.push(line["segment"], line["i"], file_name))
      elif line["type"] == "C_POP":
        file.write(self.pop(line["segment"], line["i"], file_name))
      elif line["type"] == "CONTROL":
        file.write(self.control(line["command"], line["label"], file_name))
      elif line["type"] == "FUN_CALLING":
        if line["command"] in ["function", "call"]:
          file.write(self.fun_calling(line["command"], line["function_name"], line["ArgsOrVars"], file_name))
        else:
          file.write(self.fun_calling(line["command"], "", "", file_name))
      else:
        # for debugging
        file.write(f"// error")
    file.close()
    return
  
  def Hack_init(self):
    label = f"{self.functionName}$ret.{self.call_count}"
    self.call_count += 1
    # assembly code
    SP_256 = "@256\nD=A\n@SP\nM=D\n"
    returnAddr = f"@{label}\nD=A\n@SP\nAM=M+1\nA=A-1\nM=D\n"
    save_state = "@LCL\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n@ARG\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n@THIS\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n@THAT\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n"
    reposition = f"@5\nD=A\n@SP\nD=M-D\n@ARG\nM=D\n@SP\nD=M\n@LCL\nM=D\n"
    gotoAndJMP = f"@{self.functionName}\n0;JMP\n({label})\n"
    return SP_256 + returnAddr + save_state + reposition + gotoAndJMP


  def control(self, command, label, file_name):
    if command == "label":
      return f"({file_name}.{self.functionName}${label})\n"
    elif command == "goto":
      return f"@{file_name}.{self.functionName}${label}\n0;JMP\n"
    else: # if-goto
      return f"@SP\nAM=M-1\nD=M\n@{file_name}.{self.functionName}${label}\nD;JNE\n"
  
  def fun_calling(self, command, function_name, ArgsOrVars, file_name):
    if command == "function":
      self.functionName = function_name
      # maybe I just can move SP nVars times, I'm not sure
      zeros = ""
      for _ in range(int(ArgsOrVars)):
        zeros += "@SP\nAM=M+1\nA=A-1\nM=0\n"
      # just function name (each function has to be named file_name.function_name way in vm file)
      # return f"({file_name}.{function_name})\n" + zeros
      return f"({function_name})\n" + zeros
    elif command == "call":
      label = f"{file_name}.{function_name}$ret.{self.call_count}"
      ArgsAdd5 = int(ArgsOrVars) + 5
      self.call_count += 1
      # assembly code
      returnAddr = f"@{label}\nD=A\n@SP\nAM=M+1\nA=A-1\nM=D\n"
      save_state = "@LCL\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n@ARG\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n@THIS\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n@THAT\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n"
      reposition = f"@{ArgsAdd5}\nD=A\n@SP\nD=M-D\n@ARG\nM=D\n@SP\nD=M\n@LCL\nM=D\n"
      # just function name (each function has to be named file_name.function_name way in vm file)
      gotoAndJMP = f"@{function_name}\n0;JMP\n({label})\n"
      return returnAddr + save_state + reposition + gotoAndJMP
    else: # return
      variables = "@LCL\nD=M\n@endFrame\nM=D\n@5\nA=D-A\nD=M\n@retAddr\nM=D\n@SP\nAM=M-1\nD=M\n@ARG\nA=M\nM=D\n@ARG\nD=M\n@SP\nM=D+1\n"
      restore_segments = "@endFrame\nD=M-1\nAM=D\nD=M\n@THAT\nM=D\n@endFrame\nD=M-1\nAM=D\nD=M\n@THIS\nM=D\n@endFrame\nD=M-1\nAM=D\nD=M\n@ARG\nM=D\n@endFrame\nD=M-1\nAM=D\nD=M\n@LCL\nM=D\n"
      gotoAndJMP = "@retAddr\nA=M\n0;JMP\n"
      return variables + restore_segments + gotoAndJMP
  
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