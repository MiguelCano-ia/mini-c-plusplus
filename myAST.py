from __future__ import annotations
from dataclasses import dataclass,field
from multimethod import multimeta
from typing import List, Union

from graphviz import Digraph
from lexer import Lexer
'''
Clases abstractas para el AST
'''

@dataclass
class Visitor (metaclass = multimeta):
  pass

@dataclass
class Node:
  def accept(self, visitor: Visitor):
    return visitor.visit(self, *args, **kwargs)
  
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
  ident : str
  params : List[VarDecl] = field(default_factory = list)
  body : List[Statement] = field(default_factory = list)
  
@dataclass
class VarDecl(Declaration):
  ident : str
  var_type : str
  expr : Expression = None
  
@dataclass
class ClassDecl(Declaration):
  ident : str
  super_class : str
  body : List[Statement] = field(default_factory = list)

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
class NullStmt (Statement):
  pass

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
class PrintStmt(Statement):
  expr : Expression
  
@dataclass
class ContinueStmt(Statement):
  pass

@dataclass
class NewStmt(Statement):
  class_type : str
  ident : str
  args : List[Expression] = field(default_factory = list)
  is_heap : bool = False
  
@dataclass
class SizeStmt(Statement):
  ident : str


@dataclass
class ThisStmt(Statement):
  pass

@dataclass
class SuperStmt(Statement):
  pass

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
class ConstExpr(Expression):
  value : Union[int, float, bool, str]
  
@dataclass
class VarExpr(Expression):
  ident : str
  
@dataclass
class ArrayLookupExpr(Expression):
  ident : VarExpr
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
class CallExpr(Expression):
  ident : str
  args : List[Expression] = field(default_factory = list)
  
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
class GroupingExpr(Expression):
  expr: Expression
  


@dataclass
class MakeDot(Visitor):
  
  node_default = {
    'shape': 'box',
    'style': 'filled',
    'fillcolor': 'lightblue',
    'fontcolor': 'black'
  }

  edge_default = {
    'arrowhead': 'none'
  }

  def __post_init__(self):
    self.dot = Digraph()  # Crear una nueva instancia de Digraph para cada diagrama.
    self.dot.attr('node', **self.node_default)
    self.dot.attr('edge', **self.edge_default)
    self.sequence = 0  # Reiniciar la secuencia de nodos.

  def name(self):
    """Generar nombres únicos para los nodos del diagrama."""
    self.sequence += 1
    return f'n{self.sequence}'
  
  def visit(self, cd: ClassDecl):
    node = self.name()
    self.dot.node(node, label = f'ClassDecl {cd.ident}\nSuperClass {cd.super_class}')
    for stmt in cd.body:
      self.dot.edge(node, stmt.accept(stmt))
    return node
  
  def visit(self, fd: FuncDecl):
    node = self.name()
    self.dot.node(node, label = f'FuncDecl {fd.ident}\nParams {fd.params}')
    self.dot.edge(node, self.accept(fd.body))
    return node

  def visit(self, vd: VarDecl):
    node = self.name()
    self.dot.node(node, label = f'VarDecl {vd.ident}\nType {vd.var_type}')
    if node.expr:
      self.dot.edge(node, self.visit(node.expr), label = 'init')
    return node
  
  def visit(self, p: Program):
    node = self.name()
    self.dot.node(node, label = 'Program')
    for stmt in p.stmts:
      self.dot.edge(node, self.accept(stmt))
      
  def visit(self, es: ExprStmt):
    node = self.name()
    self.dot.node(node, label = 'ExprStmt')
    self.dot.edge(node, self.accept(es.expr))
    return node
  
  def visit(self, ns: NullStmt):
    node = self.name()
    self.dot.node(node, label = 'NullStmt')
    return node
  
  def visit(self, i: IfStmt):
    node = self.name()
    self.dot.node(node, label = 'IfStmt')
    self.dot.edge(node, self.accept(i.cond), label = 'cond')
    
    if i.then_stmt:
      self.dot.edge(node, self.accept(i.then_stmt), label = 'then')
    if i.else_stmt:
      self.dot.edge(node, self.accept(i.else_stmt), label = 'else')
    else:
      null_stmt = NullStmt()
      self.dot.edge(node, self.accept(null_stmt))
    return node
  
  def visit(self, rs: ReturnStmt):
    node = self.name()
    self.dot.node(node, label = 'ReturnStmt')
    if rs.expr:
      self.dot.edge(node, self.accept(rs.expr))
    return node
  
  def visit(self, bs: BreakStmt):
    node = self.name()
    self.dot.node(node, label = 'BreakStmt')
    return node
  
  def visit(self, ws: WhileStmt):
    node = self.name()
    self.dot.node(node, label = 'WhileStmt')
    self.dot.edge(node, self.accept(ws.cond), label = 'cond')
    self.dot.edge(node, self.accept(ws.body), label = 'body')
    return node
  
  def visit(self, ps: PrintStmt):
    node = self.name()
    self.dot.node(node, label = 'PrintStmt')
    self.dot.edge(node, self.accept(ps.expr))
    return node
  
  def visit(self, cs: ContinueStmt):
    node = self.name()
    self.dot.node(node, label = 'ContinueStmt')
    return node
  
  def visit(self, ns: NewStmt):
    node = self.name()
    if ns.is_heap:
      self.dot.node(node, label = f'{ns.ident} = new {ns.class_type}[{ns.args}]')
    else:
      self.dot.node(node, label = f'{ns.ident} {ns.class_type}({ns.args})') 
    return node
  
  def visit(self, ss: SizeStmt):
    node = self.name()
    self.dot.node(node, label = f'SizeStmt {ss.ident}')
    return node
  
  def visit(self, ts: ThisStmt):
    node = self.name()
    self.dot.node(node, label = 'ThisStmt')
    return node
  
  def visit(self, ss: SuperStmt):
    node = self.name()
    self.dot.node(node, label = 'SuperStmt')
    return node
  
  def visit(self, ps: PrivateStmt):
    node = self.name()
    self.dot.node(node, label = 'PrivateStmt')
    return node
  
  def visit(self, ps: PublicStmt):
    node = self.name()
    self.dot.node(node, label = 'PublicStmt')
    return node

  def visit(self, ce: ConstExpr):
    node = self.name()
    self.dot.node(node, label = f'ConstExpr {ce.value}')
    return node
  def generate_dot(self, node):
    self.dot.save('ast.dot')
    return self.dot.source
