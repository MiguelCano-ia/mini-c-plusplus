from dataclasses import dataclass
import sly
from rich import print
from lexer import Lexer
from myAST import *

class Parser (sly.Parser):
  debugfile = 'minicpp.txt'
  
  tokens = Lexer.tokens
  
  precedence = (
    
    
  )
  