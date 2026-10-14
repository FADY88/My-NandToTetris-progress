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



class CompilationEngine:
  def __init__(self, file_name : str, tokenizer):
    self.tokenizer = tokenizer
    self.output(file_name)
  
  def output(self, file_name):
    # logic of opening the file
    with open(file_name + "_FadyT.xml", "w") as file:
      file.write("<tokens>\n")
      for token in self.tokenizer.tokens:
        file.write(self.__xmlTag(token))
      file.write("</tokens>\n")
    # edit at the end to write into the file after the call of compileClass()
    # after passing the tests, I'm too lazy to do that
    with open(file_name + "_Fady.xml", "w") as file:
      file.write(self.compileClass())
    
    return
  
  
  def compileClass(self):
    text = "<class>\n"
    
    text += self.__eat("class")
    
    text += self.__eat(self.tokenizer.getToken())
    
    text += self.__eat("{")
    
    while self.tokenizer.getToken() in ["static", "field"]:
      text += self.compileClassVarDec()
    
    while self.tokenizer.getToken() in ["constructor", "function", "method"]:
      text += self.compileSubroutineDec()
    
    text += self.__eat("}")
    
    text += "</class>\n"
    return text
  
  def compileClassVarDec(self):
    text = "<classVarDec>\n"
    
    text += self.__eat(["static", "field"])
    
    text += self.__eat(["int", "char", "boolean", self.tokenizer.getToken()])
    
    text += self.__eat(self.tokenizer.getToken())
    
    while self.tokenizer.getToken() == ",":
      text += self.__eat(",")
      text += self.__eat(self.tokenizer.getToken())
    
    text += self.__eat(";")
    
    text += "</classVarDec>\n"
    return text
  
  def compileSubroutineDec(self):
    text = "<subroutineDec>\n"
    
    text += self.__eat(["constructor", "function", "method"])
    
    text += self.__eat(["void", self.tokenizer.getToken()])
    
    text += self.__eat(self.tokenizer.getToken())
    
    text += self.__eat("(")
    
    text += self.compileParameterList()
    
    text += self.__eat(")")
    
    text += self.compileSubroutineBody()
    
    text += "</subroutineDec>\n"
    return text
  
  def compileParameterList(self):
    text = "<parameterList>\n"
    
    if self.tokenizer.getToken() != ")":
      text += self.__eat(["int", "char", "boolean", self.tokenizer.getToken()])
      text += self.__eat(self.tokenizer.getToken())
      while self.tokenizer.getToken() == ",":
        text += self.__eat(",")
        text += self.__eat(["int", "char", "boolean", self.tokenizer.getToken()])
        text += self.__eat(self.tokenizer.getToken())
    
    text += "</parameterList>\n"
    return text
  
  def compileSubroutineBody(self):
    text = "<subroutineBody>\n"
    
    text += self.__eat("{")
    
    while self.tokenizer.getToken() == "var":
      text += self.compileVarDec()
    
    text += self.compileStatements()
    
    text += self.__eat("}")
    
    text += "</subroutineBody>\n"
    return text
  
  def compileVarDec(self):
    text = "<varDec>\n"
    
    text += self.__eat("var")
    
    text += self.__eat(["int", "char", "boolean", self.tokenizer.getToken()])
    
    text += self.__eat(self.tokenizer.getToken())
    
    while self.tokenizer.getToken() == ",":
      text += self.__eat(",")
      text += self.__eat(self.tokenizer.getToken())
    
    text += self.__eat(";")
    
    text += "</varDec>\n"
    return text
  ##
  def compileStatements(self):
    # warning: match works on python 3.10 or above
    text = "<statements>\n"
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
    text += "</statements>\n"
    return text
  
  def compileLet(self):
    text = "<letStatement>\n"
    
    text += self.__eat("let")
    
    text += self.__eat(self.tokenizer.getToken())
    
    if self.tokenizer.getToken() == "[":
      text += self.__eat("[")
      text += self.compileExpression()
      text += self.__eat("]")
    
    text += self.__eat("=")

    text += self.compileExpression()
    
    text += self.__eat(";")
    
    text += "</letStatement>\n"
    return text
  
  def compileIf(self):
    text = "<ifStatement>\n"
    
    text += self.__eat("if")
    
    text += self.__eat("(")
    
    text += self.compileExpression()
    
    text += self.__eat(")")
    
    text += self.__eat("{")
    
    text += self.compileStatements()
    
    text += self.__eat("}")
    
    if self.tokenizer.getToken() == "else":
      text += self.__eat("else")
      text += self.__eat("{")
      text += self.compileStatements()
      text += self.__eat("}")
    
    text += "</ifStatement>\n"
    return text
  
  def compileWhile(self):
    text = "<whileStatement>\n"
    
    text += self.__eat("while")
    
    text += self.__eat("(")
    
    text += self.compileExpression()
    
    text += self.__eat(")")
    
    text += self.__eat("{")
    
    text += self.compileStatements()
    
    text += self.__eat("}")
    
    text += "</whileStatement>\n"
    return text
  
  def compileDo(self):
    text = "<doStatement>\n"
    
    text += self.__eat("do")
    # subroutineCall
    if self.tokenizer.getToken(1) == ".":
      text += self.__eat(self.tokenizer.getToken())
      text += self.__eat(".")
    text += self.__eat(self.tokenizer.getToken())
    text += self.__eat("(")
    text += self.compileExpressionList()
    text += self.__eat(")")
    # subroutineCall
    
    text += self.__eat(";")
    text += "</doStatement>\n"
    return text
  
  def compileReturn(self):
    text = "<returnStatement>\n"
    
    text += self.__eat("return")
    if self.tokenizer.getToken() != ";":
      text += self.compileExpression()
    
    text += self.__eat(";")
    text += "</returnStatement>\n"
    return text
  ##
  def compileExpression(self):
    text = "<expression>\n"
    
    text += self.compileTerm()
    
    while self.tokenizer.getToken() in ["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="]:
      text += self.__eat(self.tokenizer.getToken())
      text += self.compileTerm()
    
    text += "</expression>\n"
    return text
  
  def compileTerm(self):
    text = "<term>\n"
    # unaryOp term
    if self.tokenizer.getToken() in ["-", "~"]:
      text += self.__eat(self.tokenizer.getToken())
      text += self.compileTerm()
    # '('exp')'
    elif self.tokenizer.getToken() == "(":
      text += self.__eat("(")
      text += self.compileExpression()
      text += self.__eat(")")
    # varName'['exp']'
    elif self.tokenizer.getToken(1) == "[":
      text += self.__eat(self.tokenizer.getToken())
      text += self.__eat("[")
      text += self.compileExpression()
      text += self.__eat("]")
    # subroutineCall
    elif self.tokenizer.getToken(1) in ["(", "."]:
      if self.tokenizer.getToken(1) == ".":
        text += self.__eat(self.tokenizer.getToken())
        text += self.__eat(".")
      text += self.__eat(self.tokenizer.getToken())
      text += self.__eat("(")
      text += self.compileExpressionList()
      text += self.__eat(")")
    # keyword, integerConstant, stringConstant, varName
    elif self.tokenizer.getToken() in ["true", "false", "null", "this"] or self.tokenizer.tokenType() in ["integerConstant", "stringConstant", "identifier"]:
      text += self.__eat(self.tokenizer.getToken())
    else:
      print(f"Unknown Error with token ({self.tokenizer.getToken()})")
      exit(1)
    text += "</term>\n"
    return text
  
  def compileExpressionList(self):
    text = "<expressionList>\n"
    if self.tokenizer.getToken() != ")":
      text += self.compileExpression()
      while self.tokenizer.getToken() == ",":
        text += self.__eat(",")
        text += self.compileExpression()
    text += "</expressionList>\n"
    return text
  
  def __eat(self, token):
    # test with taking list[str]
    if self.tokenizer.getToken() not in token and self.tokenizer.getToken() != token:
      print(f"The token : ({self.tokenizer.getToken()}) doesn't match the pattern, expected ({token})")
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
    return f"<{element}> {token} </{element}>\n"



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
    for char in line:
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