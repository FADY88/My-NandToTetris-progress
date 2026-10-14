from sys import argv
import os

def main():
  # Check if the correct number of arguments is provided
  if len(argv) != 2:
    print("Usage: python SyntaxAnalyzer.py [FILENAME.jack | DIRECTORY]")
    return
  
  # Get the path from command-line arguments
  path = argv[1]

  files = [] # list[dict] like this [{"name" : file_name, "data": [file_data]}, ...]
  # Check if the path is a file or a directory
  if os.path.isfile(path) and path.endswith('.jack'):
    # If it's a file, process it directly
    files = process_file(path)
  elif os.path.isdir(path):
    # If it's a directory, process all files with the specified extension
    files = process_directory(path)
  else:
    print('Error: The provided path is neither a .jack file nor a directory.')
    return
  
  for file in files:
    tokenizer = JackTokenizer(file["data"])
    file["name"] = file["name"].removesuffix(".jack")
    CompilationEngine(file["name"], tokenizer)
  
  return

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
  
  return [{"name" : file_path, "data" : data}]

def process_directory(directory):
  # Hardcoded file extension
  extension = '.jack'
  data = []
  # Traverse the directory recursively
  for root, dirs, files in os.walk(directory):
    for file in files:
      if file.endswith(extension):
        file_path = os.path.join(root, file)
        data += process_file(file_path)
  return data

class Tables:
  def __init__(self):
    # {varName : {"type" : type, "kind" : kind, "#" : #}, ...}
    self.classTable = {}
    self.subroutineTable = {}
    
    self.counts = {"static" : 0, "field" : 0, "argument" : 0, "local" : 0}
  
  def startSubroutine(self):
    self.subroutineTable.clear()
    self.counts["local"] = 0
    self.counts["argument"] = 0
  
  def define(self, name, type, kind):
    if kind in ["static", "field"]:
      newKind = "this" if kind == "field" else kind
      self.classTable[name] = {"type" : type, "kind" : newKind, "index" : self.counts[kind]}
      self.counts[kind] += 1
    elif kind in ["local", "argument"]:
      self.subroutineTable[name] = {"type" : type, "kind" : kind, "index" : self.counts[kind]}
      self.counts[kind] += 1
    else:
      print("Kind defining Error")
      exit(1)
  
  def kindCount(self, kind):
    if kind in ["static", "field", "local", "argument"]:
      return self.counts[kind]
    else:
      print("Kind counting Error")
      exit(1)
  
  def kindOf(self, name):
    if name in self.subroutineTable:
      return self.subroutineTable[name]["kind"]
    elif name in self.classTable:
      return self.classTable[name]["kind"]
    else:
      print("Using a not declared variable Error Kind")
      exit(1)
  
  def typeOf(self, name):
    if name in self.subroutineTable:
      return self.subroutineTable[name]["type"]
    elif name in self.classTable:
      return self.classTable[name]["type"]
    else:
      return None
  
  def indexOf(self, name):
    if name in self.subroutineTable:
      return self.subroutineTable[name]["index"]
    elif name in self.classTable:
      return self.classTable[name]["index"]
    else:
      print("Using a not declared variable Error Index")
      exit(1)


class CompilationEngine:
  def __init__(self, file_name : str, tokenizer):
    self.tokenizer = tokenizer
    self.className = ""
    self.classSize = 0
    self.labelCount = 0
    self.tables = Tables()
    self.output(file_name)
  
  def output(self, file_name):
    with open(file_name + "2.vm", "w") as file:
      file.write(self.compileClass()[:-1])
    
    return
  
  
  def compileClass(self):
    text = ""
    
    self.__eat("class")
    
    self.className = self.tokenizer.getToken()
    self.__eat(self.tokenizer.getToken())
    
    self.__eat("{")
    
    while self.tokenizer.getToken() in ["static", "field"]:
      text += self.compileClassVarDec()
    
    self.classSize = len(self.tables.classTable)
    
    while self.tokenizer.getToken() in ["constructor", "function", "method"]:
      text += self.compileSubroutineDec()
    
    self.__eat("}")
    
    return text
  
  def compileClassVarDec(self):
    text = ""
    
    kind = self.tokenizer.getToken()
    self.__eat(["static", "field"])
    
    type = self.tokenizer.getToken()
    self.__eat(["int", "char", "boolean", self.tokenizer.getToken()])
    
    name = self.tokenizer.getToken()
    self.tables.define(name, type, kind)
    
    self.__eat(self.tokenizer.getToken())
    
    
    while self.tokenizer.getToken() == ",":
      self.__eat(",")
      name = self.tokenizer.getToken()
      self.tables.define(name, type, kind)
      
      self.__eat(self.tokenizer.getToken())
    
    self.__eat(";")
    return text
  
  def compileSubroutineDec(self):
    init = ""
    
    self.tables.startSubroutine()
    
    if self.tokenizer.getToken() == "constructor":
      init += f"push constant {self.tables.kindCount("field")}\ncall Memory.alloc 1\npop pointer 0\n"
    
    if self.tokenizer.getToken() == "method":
      init += "push argument 0\npop pointer 0\n"
      self.tables.define("this", self.className, "argument")

    self.__eat(["constructor", "function", "method"])
    self.__eat(["void", self.tokenizer.getToken()])
    
    name = self.tokenizer.getToken()
    self.__eat(self.tokenizer.getToken())
    
    self.__eat("(")
    
    self.compileParameterList()
    
    self.__eat(")")
    
    body = self.compileSubroutineBody()
    name = f"function {self.className}.{name} {self.tables.kindCount("local")}\n"
    text = name + init + body
    return text
  
  def compileParameterList(self):
    text = ""
    
    if self.tokenizer.getToken() != ")":
      type = self.tokenizer.getToken()
      
      self.__eat(["int", "char", "boolean", self.tokenizer.getToken()])
      
      name = self.tokenizer.getToken()
      
      self.tables.define(name, type, "argument")
      self.__eat(self.tokenizer.getToken())
      
      while self.tokenizer.getToken() == ",":
        self.__eat(",")
        type = self.tokenizer.getToken()
        self.__eat(["int", "char", "boolean", self.tokenizer.getToken()])
        name = self.tokenizer.getToken()
        self.tables.define(name, type, "argument")
        self.__eat(self.tokenizer.getToken())
    
    return text
  
  def compileSubroutineBody(self):
    text = ""
    
    self.__eat("{")
    
    while self.tokenizer.getToken() == "var":
      text += self.compileVarDec()
    
    text += self.compileStatements()
    
    self.__eat("}")
    
    return text
  
  def compileVarDec(self):
    text = ""
    
    self.__eat("var")
    
    type = self.tokenizer.getToken()
    self.__eat(["int", "char", "boolean", self.tokenizer.getToken()])
    
    name = self.tokenizer.getToken()
    self.tables.define(name, type, "local")
    
    self.__eat(self.tokenizer.getToken())
    while self.tokenizer.getToken() == ",":
      self.__eat(",")
      name = self.tokenizer.getToken()
      self.tables.define(name, type, "local")
      self.__eat(self.tokenizer.getToken())
    
    self.__eat(";")

    return text
  ##
  def compileStatements(self):
    # warning: match works on python 3.10 or above
    text = ""
    while True:
      token = self.tokenizer.getToken()
      match token:
        case "let":
          text += self.compileLet()
        case "if":
          text += self.compileIf()
        case "while":
          text += self.compileWhile()
        case "do":
          text += self.compileDo()
        case "return":
          text += self.compileReturn()
        case default:
          break
    return text
  
  def compileLet(self):
    text = ""
    
    self.__eat("let")
    
    name = self.tokenizer.getToken()
    self.__eat(self.tokenizer.getToken())
    
    
    if self.tokenizer.getToken() == "[":
      self.__eat("[")
      text += self.compileExpression()
      text += f"push {self.tables.kindOf(name)} {self.tables.indexOf(name)}\n"
      self.__eat("]")
      text += "add\n"
      self.__eat("=")
      text += self.compileExpression()
      text += "pop temp 0\npop pointer 1\npush temp 0\npop that 0\n"
      self.__eat(";")
      return text
    
    
    self.__eat("=")

    text += self.compileExpression()
    text += f"pop {self.tables.kindOf(name)} {self.tables.indexOf(name)}\n"
    self.__eat(";")
    
    return text
  
  def compileIf(self):
    text = ""
    
    self.__eat("if")
    self.__eat("(")
    
    text += self.compileExpression()
    text += "not\n"
    l2 = self.labelGen()
    l1 = self.labelGen()
    text += f"if-goto {l1}\n"
    self.__eat(")")
    self.__eat("{")
    
    text += self.compileStatements()
    text += f"goto {l2}\n"
    self.__eat("}")
    
    text += f"label {l1}\n"
    if self.tokenizer.getToken() == "else":
      self.__eat("else")
      self.__eat("{")
      text += self.compileStatements()
      self.__eat("}")
    
    text += f"label {l2}\n"
    return text
  
  def compileWhile(self):
    l1 = self.labelGen()
    l2 = self.labelGen()
    text = f"label {l1}\n"
    
    self.__eat("while")
    self.__eat("(")
    
    text += self.compileExpression()
    text += f"not\nif-goto {l2}\n"
    
    self.__eat(")")
    self.__eat("{")
    
    text += self.compileStatements()
    text += f"goto {l1}\nlabel {l2}\n"
    self.__eat("}")
    
    return text
  
  def compileDo(self):
    self.__eat("do")
    text = ""
    subroutineName = ""
    isThis = 0
    if self.tokenizer.getToken(1) == ".":
      subroutineName = self.tokenizer.getToken()
      self.__eat(self.tokenizer.getToken())
      self.__eat(".")
      if self.tables.typeOf(subroutineName) != None:
        text += f"push {self.tables.kindOf(subroutineName)} {self.tables.indexOf(subroutineName)}\n"
        subroutineName = self.tables.typeOf(subroutineName)
        isThis = 1
        # call varType.meth k+1
      # call varClass.fun k
      
    else:
      subroutineName = self.className
      text += "push pointer 0\n"
      isThis = 1
      # call className.meth k+1
    
    
    subroutineName += "." + self.tokenizer.getToken()
    self.__eat(self.tokenizer.getToken())
    self.__eat("(")
    tmp, countOfArgs = self.compileExpressionList()
    text += tmp
    self.__eat(")")
    
    self.__eat(";")
    text += f"call {subroutineName} {countOfArgs + isThis}\npop temp 0\n"
    return text
  
  def compileReturn(self):
    text = ""
    
    self.__eat("return")
    if self.tokenizer.getToken() != ";":
      text += self.compileExpression()
      text += "return\n"
      self.__eat(";")
      return text
    
    self.__eat(";")
    text += "push constant 0\nreturn\n"
    return text
  ##
  def compileExpression(self):
    text = self.compileTerm()
    
    while self.tokenizer.getToken() in ["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="]:
      op = self.tokenizer.getToken()
      self.__eat(op)
      text += self.compileTerm()
      text += self.getArithmetic(op)
    
    return text
  
  def getArithmetic(self, command):
    return {"+"     : "add",
            "-"     : "sub",
            "*"     : "call Math.multiply 2",
            "/"     : "call Math.divide 2",
            "&amp;" : "and",
            "|"     : "or",
            "&lt;"  : "lt",
            "&gt;"  : "gt",
            "="     : "eq"}[command] + "\n"
  
  def compileTerm(self):
    text = ""
    token = self.tokenizer.getToken()
    # unaryOp term
    if token in ["-", "~"]:
      op = token
      self.__eat(op)
      op = {"-" : "neg", "~" : "not"}[op]
      # op = "neg" if op == "-" else "not"
      text += self.compileTerm()
      text += op + "\n"
    # '('exp')'
    elif token == "(":
      self.__eat("(")
      text += self.compileExpression()
      self.__eat(")")
    # varName'['exp']'
    elif self.tokenizer.getToken(1) == "[":
      name = self.tokenizer.getToken()
      self.__eat(self.tokenizer.getToken())
      self.__eat("[")
      text += self.compileExpression()
      text += f"push {self.tables.kindOf(name)} {self.tables.indexOf(name)}\n"
      self.__eat("]")
      text += "add\npop pointer 1\npush that 0\n"
    # subroutineCall
    elif self.tokenizer.getToken(1) in ["(", "."]:
      subroutineName = ""
      isThis = 0
      if self.tokenizer.getToken(1) == ".":
        subroutineName = self.tokenizer.getToken()
        self.__eat(self.tokenizer.getToken())
        self.__eat(".")
        if self.tables.typeOf(subroutineName) != None:
          text += f"push {self.tables.kindOf(subroutineName)} {self.tables.indexOf(subroutineName)}\n"
          subroutineName = self.tables.typeOf(subroutineName)
          isThis = 1
          # call varType.meth k+1
        # call varClass.fun k
        
      else:
        subroutineName = self.className
        text += "push pointer 0\n"
        isThis = 1
        # call className.meth k+1
      
      
      subroutineName += "." + self.tokenizer.getToken()
      self.__eat(self.tokenizer.getToken())
      self.__eat("(")
      tmp, countOfArgs = self.compileExpressionList()
      text += tmp
      self.__eat(")")
      
      text += f"call {subroutineName} {countOfArgs + isThis}\n"
    # keyword
    elif token in ["true", "false", "null", "this"]:
      self.__eat(token)
      text += "push " + {"true" : "constant 1\nneg", "false" : "constant 0", "null" : "constant 0", "this" : "pointer 0"}[token] + "\n"
    # IntegerConstant
    elif token.isdigit():
      self.__eat(token)
      text += f"push constant {token}\n"
    # stringConstant
    elif self.tokenizer.tokenType() == "stringConstant":
      self.__eat(token)
      token = token[1:-1]
      text += f"push constant {len(token)}\ncall String.new 1\n"
      for c in token:
        text += f"push constant {ord(c)}\ncall String.appendChar 2\n"
    # varName
    elif self.tokenizer.tokenType() == "identifier":
      self.__eat(token)
      text += f"push {self.tables.kindOf(token)} {self.tables.indexOf(token)}\n"
    else:
      print(f"Unknown Error with token ({token})")
      exit(1)
    return text
  
  def compileExpressionList(self):
    countOfArgs = 0
    text = ""
    if self.tokenizer.getToken() != ")":
      countOfArgs += 1
      text += self.compileExpression()
      while self.tokenizer.getToken() == ",":
        countOfArgs += 1
        self.__eat(",")
        text += self.compileExpression()
    
    return text, countOfArgs
  
  def __eat(self, token):
    # test with taking list[str]
    if self.tokenizer.getToken() not in token and self.tokenizer.getToken() != token:
      print(f"in Class ({self.className}) The token : ({self.tokenizer.getToken()}) doesn't match the pattern, expected ({token})")
      print(f"({self.tokenizer.getToken(-1)}) ({self.tokenizer.getToken(1)})")
      exit(1)
    elif not self.tokenizer.hasMoreTokens():
      print("NOT ENOUGH TOKENS")
      exit(1)
    else:
      s = self.__xmlTag()
      self.tokenizer.advance()
      return s

  def __xmlTag(self, token = None):
    if token == None:
      token = self.tokenizer.getToken()
    
    element = self.tokenizer.tokenType(token)
    if token.startswith('"') and token.endswith('"'):
      token = token[1:-1]
    if element == "identifier":
      category = self.__category(token)
      return f"<{element}> {{{token} : {category}}} </{element}>\n"

    return f"<{element}> {token} </{element}>\n"
  
  def labelGen(self):
    l = f"{self.className}_{self.labelCount}"
    self.labelCount += 1
    return l
  
  def __category(self, name):
    if name in self.tables.subroutineTable:
      return self.tables.subroutineTable[name]
    elif name in self.tables.classTable:
      return self.tables.classTable[name]
    elif self.tokenizer.getToken(-1) == "class":
      return "class"
    else:
      return "subroutine"


class JackTokenizer:
  def __init__(self, lines):
    self.tokens = [] # list of tokens
    self.tokenize(lines) # store tokens in self.tokens
    self.currentIndex = 0
    # self.currentType = None # will be discussed (after discussing it's not needed)

  def tokenize(self, lines : list[str]):
    # comments with // and /*
    comment = False
    for line in lines:
      line = line.strip()

      if line.startswith("/*"):
        if not line.endswith("*/"):
          comment = True
        continue
      elif line.endswith("*/"):
        comment = False
        continue
      elif line.startswith("//") or comment or line == "":
        continue
      # middle line comments (can be inside a string, will be moved to tokenizeLine())
      # after more thinking I don't need this check (C-style syntax means ; at the end 😀)
      #
      # now in the code generation phase I discovered that I need that check because of middle line comments in lines that don't end with ;
      # I put the check in tokenizeLine() using enumerate()
      # commentIndex = line.find("//")
      # if commentIndex == -1:
      #   self.tokenizeLine(line[0:commentIndex].strip)
      # else:
      #   self.tokenizeLine(line)
      self.tokenizeLine(line)
    return
  
  def tokenizeLine(self, line : str):
    quotes = False
    temp = ""
    for i, char in enumerate(line):
      if char == '"':
        quotes = not quotes
        if quotes:
          temp = char
        else:
          self.addToken(temp + char)
          temp = ""
      elif quotes:
        temp += char
        
      elif char == " ":
        self.addToken(temp)
        temp = ""
      # // bug from the SyntaxAnalyzer -> comment after line that don't end with ; didn't get removed
      elif char == "/" and line[i + 1] == "/":
        break
      elif char in ["{", "}", "(", ")", "[", "]", ".", ",", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"]:
        self.addToken(temp)
        temp = ""
        self.addToken(self.xmlFormat(char))
      elif char.isdigit() or char.isalpha() or char == "_":
        temp += char
      # break to remove midline comments
      elif char == ";":
        self.addToken(temp)
        self.addToken(char)
        break
    if temp == "else":
      self.addToken(temp)
    return
  
  def xmlFormat(self, char):
    if char == "<":
      return "&lt;"
    elif char == ">":
      return "&gt;"
    elif char == "&":
      return "&amp;"
    else:
      return char
  
  def addToken(self, token):
    if token == "": return
    if self.tokenType(token) != "ERROR":
      self.tokens.append(token)
    return
  
  def hasMoreTokens(self):
    return not len(self.tokens) == self.currentIndex
  
  def advance(self):
    self.currentIndex += 1
    return
  
  def tokenType(self, token = None):
    token = self.getToken() if token == None else token
    if token in ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]:
      return "keyword"
    elif token in ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "=", "~"]:
      return "symbol"
    elif token.isdigit():
      return "integerConstant"
    elif token.startswith('"') and token.endswith('"'):
      return "stringConstant"
    elif self.__isValidIdentifier(token):
      return "identifier"
    else:
      return "ERROR"

  def getToken(self, index = 0):
    try:
      return self.tokens[self.currentIndex + index]
    except:
      print("NOT ENOUGH TOKENS in the future")
      exit(1)

  def __isValidIdentifier(self, s):
    if s[0].isdigit():
      return False
    for c in s[1::]:
      if not (c.isdigit() or c.isalpha() or c == "_"):
        return False
    return True


if __name__ == "__main__":
  main()