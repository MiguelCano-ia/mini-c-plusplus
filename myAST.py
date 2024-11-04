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
class ForStmt(Statement):
  var_increment : VarDecl
  cond : Expression
  increment : Expression
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
    'shape' : 'box',
    'style' : 'filled',
    'fillcolor' : 'lightblue',
    'fontcolor' : 'black',
    'font' : 'bold'
  }

  edge_default = {
    'color' : 'black',
    'arrowhead' : 'none'
  }
  
  dot = Digraph('ast')
  dot.attr('node', **node_default)
  dot.attr('edge', **edge_default)
  
  sequence = 0
  
  def name(self):  
    self.sequence += 1
    return f'n{self.sequence}'
  
  def visit(self, p : Program):
    name = self.name()
    self.dot.node(name, label = 'Program')
    for stmt in p.stmts:
      stmt_name = stmt.accept(self)
      self.dot.edge(name, stmt_name)
    return name

  def visit(self, fd : FuncDecl):
    name = self.name()
    self.dot.node(name, label = f'Function\n{fd.return_type} {fd.ident}')
    
    params_name = self.name()
    body_name = self.name()
    
    if(fd.params):
      self.dot.node(params_name, label = 'Params')
      for param in fd.params:
        param_name = param.accept(self)
        self.dot.edge(params_name, param_name)
      self.dot.edge(name, params_name)
    
    self.dot.edge(name, body_name)
    self.dot.node(body_name, label = 'Body')
    
    for stmt in fd.body:
      stmt_name = stmt.accept(self)
      self.dot.edge(body_name, stmt_name)
    
      
    return name
    
      
  def visit(self, vd : VarDecl):
    name = self.name()
    if vd.expr:
      self.dot.node(name, label = f'{vd.var_type} {vd.ident} =')
      expr_name = vd.expr.accept(self)
      self.dot.edge(name, expr_name)
    else:
      self.dot.node(name, label = f'{vd.var_type} {vd.ident}')
    return name
  
  def visit(self, cd : ClassDecl):
    name = self.name()
    if cd.super_class:
      self.dot.node(name, label = f'Class\n{cd.ident} : {cd.super_class}')
    else:
      self.dot.node(name, label = f'Class\n{cd.ident}')
    for stmt in cd.body:
      stmt_name = stmt.accept(self)
      self.dot.edge(name, stmt_name)
    return name
  
  def visit(self, ad : ArrayDecl):
    name = self.name()
    self.dot.node(name, label = f'{ad.var_type} {ad.ident}')
    size_name = self.visit(ad.size)
    self.dot.edge(name, size_name, label='Size')
    return name

  def visit(self, es : ExprStmt):
    name = self.name()
    self.dot.node(name, label = 'Expression')
    expr_name = es.expr.accept(self)
    self.dot.edge(name, expr_name)
    return name

  def visit(self, ns : NullStmt):
    name = self.name()
    self.dot.node(name, label = 'Null')
    return name
  
  def visit(self, is_ : IfStmt):
    name = self.name()
    self.dot.node(name, label = 'If')
    cond_name = is_.cond.accept(self)
    self.dot.edge(name, cond_name)
    
    return name
  
  def visit (self, rs : ReturnStmt):
    name = self.name()
    self.dot.node(name, label = 'Return')
    if rs.expr:
      expr_name = rs.expr.accept(self)
      self.dot.edge(name, expr_name)
    return name

  def visit(self, bs : BreakStmt):
    name = self.name()
    self.dot.node(name, label = 'Break')
    return name
  
  
  def visit(self, ws : WhileStmt):
    name = self.name()
    self.dot.node(name, label = 'While')
    cond_name = ws.cond.accept(self)
    self.dot.edge(name, cond_name)
    for stmt in ws.body:
      stmt_name = stmt.accept(self)
      self.dot.edge(name, stmt_name)
    return name
  
  def visit(self, fs : ForStmt):
    name = self.name()
    self.dot.node(name, label = 'For')
    var_name = fs.var_increment.accept(self)
    self.dot.edge(name, var_name)
    cond_name = fs.cond.accept(self)
    self.dot.edge(name, cond_name)
    inc_name = fs.increment.accept(self)
    self.dot.edge(name, inc_name)
    for stmt in fs.body:
      stmt_name = stmt.accept(self)
      self.dot.edge(name, stmt_name)
    return name
  
  def visit(self, ps : PrintStmt):
    name = self.name()
    self.dot.node(name, label = 'Print')
    expr_name = ps.expr.accept(self)
    self.dot.edge(name, expr_name)
    return name
  
  def visit(self, cs : ContinueStmt):
    name = self.name()
    self.dot.node(name, label = 'Continue')
    return name
  
  def visit(self, ns : NewStmt):
    name = self.name()
    self.dot.node(name, label = f'New {ns.class_type}')
    for arg in ns.args:
      arg_name = arg.accept(self)
      self.dot.edge(name, arg_name)
    return name
  
  def visit(self, ss : SizeStmt):
    name = self.name()
    self.dot.node(name, label = f'Size {ss.ident}')
    return name
  
  def vist (self, ts : ThisStmt):
    name = self.name()
    self.dot.node(name, label = 'This')
    return name
  
  def visit(self, ss : SuperStmt):
    name = self.name()
    self.dot.node(name, label = 'Super')
    for arg in ss.args_list:
      arg_name = arg.accept(self)
      self.dot.edge(name, arg_name)
    return name
  
  def visit(self, ps : PrivateStmt):
    name = self.name()
    self.dot.node(name, label = 'Private')
    return name
  
  def visit(self, ps : PublicStmt):
    name = self.name()
    self.dot.node(name, label = 'Public')
    return name
  
  def visit(self, ce : CallExpr):
    name = self.name()
    self.dot.node(name, label = f'Call {ce.ident}')
    for arg in ce.args:
      arg_name = arg.accept(self)
      self.dot.edge(name, arg_name)
    return name
  
  def visit(self, ce : ConstExpr):
    name = self.name()
    self.dot.node(name, label = f'Const {ce.value}')
    return name
  
  def visit(self, ve : VarExpr):
    name = self.name()
    self.dot.node(name, label = f'Var {ve.ident}')
    return name
  
  def visit(self, ale : ArrayLookupExpr):
    name = self.name()
    self.dot.node(name, label = 'Array Lookup')
    ident_name = ale.ident.accept(self)
    index_name = ale.index.accept(self)
    self.dot.edge(name, ident_name)
    self.dot.edge(name, index_name)
    return name
  
  def visit(self, vae : VarAssignExpr):
    name = self.name()
    self.dot.node(name, label = f'{vae.ident} =')
    expr_name = vae.expr.accept(self)
    self.dot.edge(name, expr_name)
    return name
  
  def visit(self, aae : ArrayAssignExpr):
    name = self.name()
    self.dot.node(name, label = f'{aae.ident} =')
    size_name = self.visit(aae.index)
    self.dot.edge(name, size_name, label='Size')
    return name
  
  def visit(self, ase : ArraySizeExpr):
    name = self.name()
    self.dot.node(name, label = f'Size {ase.ident}')
    return name
  
  def visit(self, itfe : IntToFloatExpr):
    name = self.name()
    self.dot.node(name, label = 'Int to Float')
    expr_name = itfe.expr.accept(self)
    self.dot.edge(name, expr_name)
    return name
  
  def visit(self, be : BinaryExpr):
    name = self.name()
    self.dot.node(name, label = f'{be.operand}')
    left_name = be.left.accept(self)
    right_name = be.right.accept(self)
    self.dot.edge(name, left_name)
    self.dot.edge(name, right_name)
    return name
  
  def visit(self, ue : UnaryExpr):
    name = self.name()
    self.dot.node(name, label = f'{ue.operand}')
    expr_name = ue.expr.accept(self)
    self.dot.edge(name, expr_name)
    return name
  
  def visit(self, ge : GroupingExpr):
    name = self.name()
    self.dot.node(name, label = 'Grouping')
    expr_name = ge.expr.accept(self)
    self.dot.edge(name, expr_name)
    return name
  
  def generate_dot(self):
    self.dot.save('ast.dot')
    self.dot.render('ast',format='png', cleanup=False)
  