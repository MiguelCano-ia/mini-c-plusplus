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
    return visitor.visit(self)
  
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
class InstanceDecl(Declaration):
  class_type: str
  instance_name: str

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
  else_cond : Expression = None
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
class CallExpr(Expression):
  ident : str
  args : List[Expression] = field(default_factory = list)
  

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
  
  #Declaraciones
  def visit(self, fd: FuncDecl):
    name = self.name()
    self.dot.node(name, f'FuncDecl \ntype: {fd.return_type} \nname: {fd.ident}')
    for param in fd.params:
        self.dot.edge(name, self.visit(param), label='param')
    for stmt in fd.body:
        self.dot.edge(name, self.visit(stmt), label='body')
    return name

  def visit(self, vd: VarDecl):
    name = self.name()
    self.dot.node(name, f'VarDecl \nname: {vd.ident} \ntype: {vd.var_type}')
    if vd.expr:
        self.dot.edge(name, self.visit(vd.expr), label='expr')
    return name

  def visit(self, cd: ClassDecl):
    name = self.name()
    self.dot.node(name, f'ClassDecl \nname: {cd.ident} \nsuper_class: {cd.super_class}')
    for stmt in cd.body:
        self.dot.edge(name, self.visit(stmt), label='body')
    return name
  
  #Acciones
  
  def visit (self, p: Program):
    name = self.name()
    self.dot.node(name, 'Program')
    for stmt in p.stmts:
      self.dot.edge(name,self.visit(stmt))
    return name
  
  def visit (self, es: ExprStmt):
    name = self.name()
    self.dot.node(name, 'ExprStmt')
    self.dot.edge(name,self.visit(es.expr))
    return name
  
  def visit (self, ns: NullStmt):
    name = self.name()
    self.dot.node(name, 'NullStmt')
    return name
  
  def visit (self, is_: IfStmt):
    name = self.name()
    self.dot.node(name, 'IfStmt')
    self.dot.edge(name,self.visit(is_.cond), label = 'cond')
    if is_.then_stmt:
      self.dot.edge(name,self.visit(is_.then_stmt), label = 'then_stmt')  
    if is_.else_stmt:
      self.dot.edge(name,self.visit(is_.else_stmt), label = 'else_stmt')
    return name
  
  def visit (self, rs: ReturnStmt):
    name = self.name()
    self.dot.node(name, 'ReturnStmt')
    if rs.expr:
      self.dot.edge(name,self.visit(rs.expr), label = 'expr')
    return name
  
  def visit (self, bs: BreakStmt):
    name = self.name()
    self.dot.node(name, 'BreakStmt')
    return name
  
  def visit (self, ws: WhileStmt):
    name = self.name()
    self.dot.node(name, 'WhileStmt')
    self.dot.edge(name,self.visit(ws.cond), label = 'cond')
    self.dot.edge(name,self.visit(ws.body), label = 'body')
    return name
  
  def visit (self, ps: PrintStmt):
    name = self.name()
    self.dot.node(name, 'PrintStmt')
    self.dot.edge(name,self.visit(ps.expr), label = 'expr')
    return name
  
  def visit (self, cs: ContinueStmt):
    name = self.name()
    self.dot.node(name, 'ContinueStmt')
    return name
  
  def visit (self, ns: NewStmt):
    name = self.name()
    if ns.is_heap:
      self.dot.node(name, f'NewStmt \nclass_type: {ns.class_type} \nident: {ns.ident} \nargs: {ns.args}')
    else:
      self.dot.node(name, f'NewStmt \nclass_type: {ns.class_type} \nident: {ns.ident} \nargs: {ns.args} \nstack')
    return name
  
  def visit (self, ss: SizeStmt):
    name = self.name()
    self.dot.node(name, f'SizeStmt \nident: {ss.ident}')
    return name

  def visit (self, ts: ThisStmt):
    name = self.name()
    self.dot.node(name, 'ThisStmt')
    return name
  
  def visit (self, ss: SuperStmt):
    name = self.name()
    self.dot.node(name, 'SuperStmt')
    return name
  
  def visit (self, ps: PrivateStmt):
    name = self.name()
    self.dot.node(name, 'PrivateStmt')
    return name
  
  def visit (self, ps: PublicStmt):
    name = self.name()
    self.dot.node(name, 'PublicStmt')
    return name
  
  def visit (self, ce: CallExpr):
    name = self.name()
    self.dot.node(name, f'CallExpr \nident: {ce.ident} \nargs: {ce.args}')
    return name
  
  def visit(self, ce: ConstExpr):
    name = self.name()
    self.dot.node(name, f'ConstExpr \nvalue: {ce.value}')
    return name

  def visit(self, ve: VarExpr):
    name = self.name()
    self.dot.node(name, f'VarExpr \nident: {ve.ident}')
    return name

  def visit(self, ale: ArrayLookupExpr):
    name = self.name()
    self.dot.node(name, f'ArrayLookupExpr\nident: {ale.ident}')
    self.dot.edge(name, self.visit(ale.index), label='index')
    return name

  def visit(self, vae: VarAssignExpr):
    name = self.name()
    self.dot.node(name, f'VarAssignExpr \nident: {vae.ident}')
    self.dot.edge(name, self.visit(vae.expr), label='expr')
    return name
  
  def visit (self, aae: ArrayAssignExpr):
    name = self.name()
    self.dot.node(name, f'ArrayAssignExpr \nident: {aae.ident}')
    self.dot.edge(name,self.visit(aae.index), label = 'index')
    self.dot.edge(name,self.visit(aae.expr), label = 'expr')
    return name
  
  def visit (self, ase: ArraySizeExpr):
    name = self.name()
    self.dot.node(name, f'ArraySizeExpr \nident: {ase.ident}')
    return name
  
  def visit (self, itfe: IntToFloatExpr):
    name = self.name()
    self.dot.node(name, 'IntToFloatExpr')
    self.dot.edge(name,self.visit(itfe.expr), label = 'expr')
    return name
  
  def visit (self, be: BinaryExpr):
    name = self.name()
    self.dot.node(name, f'BinaryExpr \noperand: {be.operand}')
    self.dot.edge(name,self.visit(be.left), label = 'left')
    self.dot.edge(name,self.visit(be.right), label = 'right')
    return name
  
  def visit (self, ue: UnaryExpr):
    name = self.name()
    self.dot.node(name, f'UnaryExpr \noperand: {ue.operand}')
    self.dot.edge(name,self.visit(ue.expr), label = 'expr')
    return name
  
  def visit (self, ge: GroupingExpr):
    name = self.name()
    self.dot.node(name, 'GroupingExpr')
    self.dot.edge(name,self.visit(ge.expr), label = 'expr')
    return name
  
  def generate_dot(self):
    self.dot.render('ast', view=True) 