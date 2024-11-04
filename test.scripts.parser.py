from lexer import *
from parser import *
from myAST import *
from rich import print
import os 

dir = './scripts'
    
def select_script():
  try:
    files = os.listdir(dir)
    if not files:
      print("No files found.")
    else:
      for i, file in enumerate(files, start = 1):
        print(f"{i}. {file}")
      print("Select a script to parse:")
      script = int(input())
      if script > 0 and script <= len(files):
        with open(f"{dir}/{files[script - 1]}", 'r') as f:
          data = f.read()
        return data
      else:
        print("[red]Invalid option.")
  except FileNotFoundError:
    print(f"[red] Directory {dir} not found.")
  except Exception as e:
    print(f"[red] Error: {e}")
    
def tryParser():
  data = select_script()
  if data:
    lexer = Lexer()
    parser = Parser()
    tokens = lexer.tokenize(data)
    
    for token in tokens:
      print(token) 
      
    tokens = lexer.tokenize(data)
    ast = parser.parse(tokens)
    
    print (ast)

    dot = MakeDot()
    
    for expr in ast.stmts:
      expr.accept(dot)
    
    ast_dot = dot.generate_dot()
    
    
    
tryParser()