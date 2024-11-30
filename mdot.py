from __future__ import annotations
from dataclasses import dataclass
from graphviz import Digraph

from myAST import *

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
    
    if(fd.return_type == None):
      self.dot.node(name, label = f'Constructor\n{fd.ident}')
    else:
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

  def visit(self, ns : NullExpr):
    name = self.name()
    self.dot.node(name, label = 'Null')
    return name
  
  def visit(self, is_ : IfStmt):
    name = self.name()
    self.dot.node(name, label='If')
    
    cond_name = self.name()
    self.dot.node(cond_name, label='Cond')
    cond_expr_name = is_.cond.accept(self)
    self.dot.edge(cond_name, cond_expr_name)
    self.dot.edge(name, cond_name)
    
    
    then_name = self.name()
    self.dot.node(then_name, label='Then')
    for stmt in is_.then_stmt:
      stmt_name = stmt.accept(self)
      self.dot.edge(then_name, stmt_name)
    self.dot.edge(name, then_name)

    if is_.else_stmt:
      else_name = self.name()
      self.dot.node(else_name, label='Else')
      
      if isinstance(is_.else_stmt, list):
        for stmt in is_.else_stmt:
          stmt_name = stmt.accept(self)
          self.dot.edge(else_name, stmt_name)
      else:
        else_stmt_name = is_.else_stmt.accept(self)
        self.dot.edge(else_name, else_stmt_name)
      
      self.dot.edge(name, else_name)
    return name

  def visit(self, rs : ReturnStmt):
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
  
  def visit(self,fs:ForStmt):
    name = self.name()
    self.dot.node(name, label = 'For')
    init_name = self.name()
    self.dot.node(init_name, label = 'Initialization')
    if isinstance(fs.initialization, VarDecl):
      decl_name = fs.initialization.accept(self)
      self.dot.edge(init_name, decl_name)
    else:
      expr_name = fs.initialization.accept(self)
      self.dot.edge(init_name, expr_name)
    self.dot.edge(name, init_name)
    
    cond_name = self.name()
    self.dot.node(cond_name, label = 'Condition')
    cond_expr_name = fs.condition.accept(self)
    self.dot.edge(cond_name, cond_expr_name)
    self.dot.edge(name, cond_name)
    
    inc_name = self.name()
    self.dot.node(inc_name, label = 'Increment')
    if isinstance(fs.increment, VarAssignExpr):
      assign_name = fs.increment.accept(self)
      self.dot.edge(inc_name, assign_name)
    else:
      expr_name = fs.increment.accept(self)
      self.dot.edge(inc_name, expr_name)
    self.dot.edge(name, inc_name)
    
    body_name = self.name()
    self.dot.node(body_name, label = 'Body')
    for stmt in fs.body:
      stmt_name = stmt.accept(self)
      self.dot.edge(body_name, stmt_name)
    self.dot.edge(name, body_name)
    return name

  def visit(self, ps : PrintStmt):
    name = self.name()
    self.dot.node(name, label = 'PrintF')
    charArr_name = self.name()
    self.dot.node(charArr_name, label = f'Format {ps.format_string}')
    
    if ps.args_list:
      args_name = self.name()
      self.dot.node(args_name, label = 'Args')
      for arg in ps.args_list:
        arg_name = arg.accept(self)
        self.dot.edge(args_name, arg_name)
      self.dot.edge(name, args_name)
    
    self.dot.edge(name, charArr_name)
    return name
    
      
  
  def visit(self, sp : SPrintStmt):
    name = self.name()
    self.dot.node(name, label = 'SPrintF')
    buffer_name = self.name()
    self.dot.node(buffer_name, label = f'Buffer {sp.buffer}')
    self.dot.edge(name, buffer_name)
    
    if sp.format_string:
      format_name = self.name()
      self.dot.node(format_name, label = f'Format {sp.format_string}')
      self.dot.edge(name, format_name)
    
    if sp.args_list:
      args_name = self.name()
      self.dot.node(args_name, label = 'Args')
      for arg in sp.args_list:
        arg_name = arg.accept(self)
        self.dot.edge(args_name, arg_name)
      self.dot.edge(name, args_name)
      
    return name
  
  def visit(self, cs : ContinueStmt):
    name = self.name()
    self.dot.node(name, label = 'Continue')
    return name
  
  def visit(self, ns : ObjectDecl):
    name = self.name()
    self.dot.node(name, label = f'Object\n{ns.class_type} {ns.instance_name}')
    if ns.args:
      args_name = self.name()
      self.dot.node(args_name, label = 'Args')
      for arg in ns.args:
        arg_name = arg.accept(self)
        self.dot.edge(args_name, arg_name)
      self.dot.edge(name, args_name)
    return name
  
  def visit(self, ss : SizeStmt):
    name = self.name()
    self.dot.node(name, label = f'Size {ss.ident}')
    return name
  
  def visit(self, ts : ThisStmt):
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
    
    if ce.object_name:
      self.dot.node(name, label = f'Call {ce.object_name}.{ce.ident}')
    else:
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
    
    ident_name = self.name()
    self.dot.node(ident_name, label = f'Ident {ale.ident}')
    self.dot.edge(name, ident_name)
    
    index_name = ale.index.accept(self)
    self.dot.edge(name, index_name, label='Index')
    
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
  
  def visit(self, node: PrefixIncExpr):
    name = self.name()
    self.dot.node(name, label='PrefixInc++')
    expr_name = node.expr.accept(self)
    self.dot.edge(name, expr_name, label='expr')
    return name

 
  def visit(self, node: PrefixDecExpr):
    name = self.name()
    self.dot.node(name, label='PrefixDec--')
    expr_name = node.expr.accept(self)
    self.dot.edge(name, expr_name, label='expr')
    return name

  def visit(self, node: PostfixIncExpr):
    name = self.name()
    self.dot.node(name, label='PostfixInc++')
    expr_name = node.expr.accept(self)
    self.dot.edge(name, expr_name, label='expr')
    return name
      
  def visit(self, node: PostfixDecExpr):
    name = self.name()
    self.dot.node(name, label='PostfixDec--')
    expr_name = node.expr.accept(self)
    self.dot.edge(name, expr_name, label='expr')
    return name
  
  def visit(self, node: ShortCircuitAndExpr):
    name = self.name()
    self.dot.node(name, label='ShortCircuitAnd')
    left_name = node.left.accept(self)
    right_name = node.right.accept(self)
    self.dot.edge(name, left_name, label='left')
    self.dot.edge(name, right_name, label='right')
    return name
  
  def visit(self, node: ShortCircuitOrExpr):
    name = self.name()
    self.dot.node(name, label='ShortCircuitOr')
    left_name = node.left.accept(self)
    right_name = node.right.accept(self)
    self.dot.edge(name, left_name, label='left')
    self.dot.edge(name, right_name, label='right')
    return name
  
  def visit(self, ue : UnaryExpr):
    name = self.name()
    self.dot.node(name, label = f'{ue.operand}')
    expr_name = ue.expr.accept(self)
    self.dot.edge(name, expr_name)
    return name
  
  def visit(self, node: CastExpr):
    name = self.name()
    self.dot.node(name, label=f'Cast to {node.target_type}')
    expr_name = node.expr.accept(self)
    self.dot.edge(name, expr_name)
    return name
  
  def visit(self, node: CompoundAssignExpr):
        name = self.name()
        self.dot.node(name, label=f'{node.ident} {node.operator}')
        expr_name = node.expr.accept(self)
        self.dot.edge(name, expr_name, label='Expr')
        return name
  
  def visit(self, ge : GroupingExpr):
    name = self.name()
    self.dot.node(name, label = 'Grouping')
    expr_name = ge.expr.accept(self)
    self.dot.edge(name, expr_name)
    return name
  
  def generate_dot(self):
    print(self.dot.source)
  
  def generate_dot_png(self):
    #Generar el archivo png en el escritorio del usuario en formato png
    
    self.dot.render('ast',format='png', cleanup=False, view=True)