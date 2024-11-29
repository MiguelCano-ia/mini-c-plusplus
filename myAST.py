from __future__ import annotations
from dataclasses import dataclass,field
from multimethod import multimeta
from typing import List, Union
'''
Clases abstractas para el AST
'''

@dataclass
class Visitor (metaclass = multimeta):
  pass

@dataclass
class Node:
  def accept(self, v: Visitor):
    return v.visit(self)
  
@dataclass
class Expression (Node):
  pass

@dataclass
class Statement (Node):
  pass

class Declaration(Statement):
  pass

'''
Clases declarativas para el AST
'''
@dataclass
class FuncDecl(Declaration):
  return_type : str
  ident : str
  params : List[VarDecl] = field(default_factory = list)
  body : List[Statement] = field(default_factory = list)
  
@dataclass
class VarDecl(Declaration):
  var_type : str
  ident : str
  expr : Expression = None
@dataclass
class ClassDecl(Declaration):
  ident : str
  super_class : str
  body : List[Statement] = field(default_factory = list)
  
@dataclass
class ArrayDecl(Declaration):
  var_type : str
  ident : str
  size : Expression
  
@dataclass
class ObjectDecl(Declaration):
  class_type: str
  instance_name: str
  args : List[Expression] = field(default_factory = list)

'''
Acciones sin valores asociados
'''
@dataclass
class Program (Statement):
  stmts: List[Statement] = field (default_factory = list)
  
@dataclass
class ExprStmt(Statement):
  expr: Expression
  
  
@dataclass
class IfStmt(Statement):
  cond : Expression
  then_stmt : List[Statement] = field(default_factory = list)
  else_stmt : List[Statement] = field(default_factory = list) 
  
@dataclass
class ReturnStmt(Statement):
  expr : Expression = None

@dataclass
class BreakStmt(Statement):
  pass

@dataclass
class WhileStmt(Statement):
  cond : Expression
  body : List[Statement] = field(default_factory = list)
  
@dataclass
class ForStmt(Statement):
  initialization: Statement  # Puede ser VarDecl o ExprStmt
  condition: Expression
  increment: Statement
  body: List[Statement] = field(default_factory = list)
  
@dataclass
class PrintStmt(Statement):
  format_string : str
  args_list : List[Expression] = field(default_factory = list)

@dataclass 
class SPrintStmt(Statement):
  buffer : VarExpr 
  format_string : str
  args_list : List[Expression] = field(default_factory = list)

@dataclass
class ContinueStmt(Statement):
  pass

@dataclass
class SizeStmt(Statement):
  ident : str

@dataclass
class ThisStmt(Statement):
  pass

@dataclass
class SuperStmt(Statement):
  args_list : List[Expression] = field(default_factory = list)
  
@dataclass
class PrivateStmt(Statement):
  pass

@dataclass
class PublicStmt(Statement):
  pass

'''
Expresiones con valores asociados
'''

@dataclass
class NullExpr(Expression):
  pass

@dataclass
class CallExpr(Expression):
  ident : str
  object_name : str = None
  args : List[Expression] = field(default_factory = list)

@dataclass
class ConstExpr(Expression):
  value : Union[int, float, bool, str]
  
@dataclass
class CompoundAssignExpr(Expression):
    ident: str
    operator: str  
    expr: Expression

@dataclass
class VarExpr(Expression):
  ident : str
    
@dataclass
class ArrayLookupExpr(Expression):
  ident : str
  index : Expression

@dataclass
class VarAssignExpr(Expression):
  ident : str
  expr : Expression
  
@dataclass
class ArrayAssignExpr(Expression):
  ident : str
  index : Expression
  expr : Expression

@dataclass
class ArraySizeExpr(Expression):
  ident : str
  
@dataclass
class IntToFloatExpr(Expression):
  expr : Expression
  
@dataclass
class BinaryExpr(Expression):
  left: Expression
  operand: str
  right: Expression
  
@dataclass
class UnaryExpr(Expression):
  operand: str
  expr: Expression
  
@dataclass
class CastExpr(Expression):
  target_type: str
  expr: Expression
  
@dataclass
class GroupingExpr(Expression):
  expr: Expression
  
@dataclass
class PrefixIncExpr(Expression):
  expr: Expression
  
@dataclass
class PrefixDecExpr(Expression):
  expr: Expression 
  
@dataclass
class PostfixIncExpr(Expression):
  expr: Expression
  
@dataclass
class PostfixDecExpr(Expression):
  expr: Expression
  
@dataclass 
class ShortCircuitAndExpr(Expression):
  left: Expression
  right: Expression
  
@dataclass
class ShortCircuitOrExpr(Expression):
  left: Expression
  right: Expression
