from dataclasses import dataclass
import sly
from rich import print
from lexer import Lexer
from myAST import *

class Parser (sly.Parser):
  debugfile = 'minicpp.txt'
  
  tokens = Lexer.tokens
  
  precedence = (
    ('left',INCREMENT,DECREMENT),
    ('right', '='),
    ('left', OR),
    ('left', AND),
    ('left', EQ, NE),
    ('left', LT, LE, GT, GE),
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', UNARY),
  )
  
  @_("{declarations}")
  def program(self, p):
    return Program(p.declarations)
  
  @_("class_declaration",
    "func_declaration",
    "var_declaration",
    "statement")
  def declaration(self, p):
    return p[0]
  
  @_("CLASS IDENT '{' class_body '}'")
  def class_declaration(self, p):
    return ClassDecl(p.ID, p.class_body)
  
  @_()