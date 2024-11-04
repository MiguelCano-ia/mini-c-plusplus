from dataclasses import dataclass
import sly
from rich import print
from lexer import Lexer
from myAST import *

class Parser(sly.Parser):
  
  debugfile = 'parser.out'
  
  tokens = Lexer.tokens
  
  precedence = (
    ('nonassoc', IFX),
    ('nonassoc', ELSE),
    ('left',INCREMENT,DECREMENT),
    ('left', '='),
    ('left', OR),
    ('left', AND),
    ('nonassoc', EQ, NE),
    ('nonassoc', LT, LE, GT, GE ),
    ('left', '+', '-'),
    ('left', '*', '/', '%'),
    ('right', 'NOT'),
    ('right', UNARY,'!')
  )
  
  # Debug para ver el proceso de parsing
  def __init__(self):
    self.debugging = True
  
  @_("decl_list")
  def program(self, p):
    return Program(p.decl_list)
  
  @_("decl_list decl")
  def decl_list(self,p):
    return p.decl_list + [p.decl]
  
  @_("decl")
  def decl_list(self,p):
    return [p.decl]

  @_("var_decl", "func_decl", "class_decl")
  def decl(self,p):
    return p[0]
  
  @_("CLASS IDENT '{' compound_stmt '}'")
  def class_decl(self,p):
    return ClassDecl(p.IDENT, p.compound_stmt)
  
  @_("type_spec IDENT '(' param_list ')' compound_stmt")
  def func_decl(self,p):
    return FuncDecl(p.type_spec, p.IDENT, p.param_list, p.compound_stmt)
  
  @_("empty")
  def param_list(self,p):
    return []
  
  @_("param_list ',' param")
  def param_list(self,p):
    return p.param_list + [p.param]
  
  @_("type_spec IDENT")
  def param(self,p):
    return VarDecl(p.type_spec, p.IDENT)
  
  @_("type_spec IDENT '[' INTLIT ']'")
  def param(self,p):
    return ArrayDecl(ident=p.IDENT, var_type=p.type_spec, size=p.INTLIT)
  
  @_("'{' local_decls stmt_list '}'")
  def compound_stmt(self,p):
    return list(p.local_decls) + list(p.stmt_list)
  
  @_("var_decl local_decls")
  def local_decls(self,p):
      return [p.var_decl] + p.local_decls
  
  @_("empty")
  def local_decls(self,p):
    return []
  
  @_("empty")
  def stmt_list(self,p):
    return []
  
  @_("stmt stmt_list")
  def stmt_list(self,p):
    return [p.stmt] + p.stmt_list
  
  @_("expr_stmt", "compound_stmt", "if_stmt", "return_stmt", "while_stmt","break_stmt", "continue_stmt", "print_stmt", "new_stmt" ,"this_stmt", "private_stmt", "public_stmt", "super_stmt", "for_stmt")
  def stmt(self,p):
    return p[0]
  
  @_("FOR '(' expr ';' expr ';' expr ')' stmt")
  def for_stmt(self,p):
    return ForStmt(p.expr0, p.expr1, p.expr2, p.stmt)
  
  @_("SUPER '(' args_list ')' ';'")
  def super_stmt(self,p):
    return SuperStmt(p.args_list)
  
  @_("expr ';'")
  def expr_stmt(self,p):
    return ExprStmt(p.expr)

  @_("IF '(' expr ')' stmt %prec IFX")
  def if_stmt(self, p):
    return IfStmt(cond=p.expr, then_stmt=p.stmt)

  @_("IF '(' expr ')' stmt ELSE stmt")
  def if_stmt(self, p):
    return IfStmt(cond=p.expr, then_stmt=p.stmt0, else_stmt=p.stmt1)
  
  @_("PRIVATE ':' stmt")
  def private_stmt(self,p):
    return PrivateStmt(p.stmt)
  
  @_("PUBLIC ':' stmt")
  def public_stmt(self,p):
    return PublicStmt(p.stmt)
  
  @_("RETURN ';'")
  def return_stmt(self,p):
    return ReturnStmt()
  
  @_("RETURN expr ';'")
  def return_stmt(self,p):
    return ReturnStmt(p.expr)
  
  @_("WHILE '(' expr ')' stmt")
  def while_stmt(self,p):
    return WhileStmt(cond=p.expr, body=p.stmt)
  
  @_("BREAK ';'")
  def break_stmt(self,p):
    return BreakStmt()
  
  @_("CONTINUE ';'")
  def continue_stmt(self,p):
    return ContinueStmt()
  
  @_("IDENT '=' NEW IDENT '(' args_list ')' ';'" )
  def new_stmt(self,p):
    return NewStmt(ident=p.IDENT, class_type=p.IDENT0, args=p.args_list)
  
  @_("empty")
  def args_list(self,p):
    return p[0]
  
  @_("args_list ',' expr")
  def args_list(self,p):
    return p.args_list + [p.expr]
  
  @_("PRINTF '(' expr ')' ';'")
  def print_stmt(self,p):
    return PrintStmt(p.expr)
  
  @_("THIS ';'")
  def this_stmt(self,p):
    return ThisStmt()
  
  @_("type_spec IDENT ';' ")
  def var_decl(self,p):
    return VarDecl(p.type_spec, p.IDENT)
  
  @_("type_spec IDENT '=' expr ';' ")
  def var_decl(self,p):
    return VarDecl(p.type_spec, p.IDENT, p.expr)
  
  @_("type_spec IDENT '[' INTLIT ']' ';' ")
  def var_decl(self,p):
    return ArrayDecl(p.type_spec,p.IDENT, p.INTLIT)
  
  @_("VOID", "INT", "FLOAT", "BOOL", "STRING")
  def type_spec(self,p):
    return p[0]
  
  @_("INTLIT", "FLOATLIT", "BOOLIT", "STRINGLIT", "TRUE", "FALSE")
  def expr(self,p):
    return ConstExpr(p[0])
  
  @_("IDENT '=' expr")
  def expr(self,p):
    return VarAssignExpr(p.IDENT, p.expr)
  
  @_("IDENT '[' expr ']' '=' expr")
  def expr(self,p):
    return ArrayAssignExpr(p.IDENT, p.expr0, p.expr1)
  
  @_("IDENT '[' expr ']'")
  def expr(self,p):
    return ArrayLookupExpr(p.IDENT, p.expr)
  
  @_("IDENT '(' args_list ')'")
  def expr(self,p):
    return CallExpr(p.IDENT, p.args_list)
  
  @_("IDENT")
  def expr(self,p):
    return VarExpr(p.IDENT)

  @_("expr OR expr",
     "expr AND expr",
     "expr EQ expr",
     "expr NE expr",
     "expr LT expr",
     "expr LE expr",
     "expr GT expr",
     "expr GE expr",
     "expr '+' expr",
     "expr '-' expr",
     "expr '*' expr",
     "expr '/' expr",
     "expr '%' expr")
  def expr(self,p):
    return BinaryExpr(p.expr0,p[1], p.expr1)
  
  
  @_("'-' expr %prec UNARY",
     "'!' expr %prec UNARY",
     "'+' expr %prec UNARY",
     "INCREMENT expr %prec UNARY",
     "DECREMENT expr %prec UNARY",
     "NOT expr %prec UNARY")
  def expr(self,p):
    return UnaryExpr(p[0], p.expr)
  
  @_("'(' expr ')'")
  def expr(self,p):
    return GroupingExpr(p.expr)
  
  @_("IDENT '.' SIZE")
  def expr(self,p):
    return ArraySizeExpr(p.IDENT)
  
   
  @_("")
  def empty(self, token):
    return NullStmt()
  
  def error(self,p):
    lineo = p.lineno if p else "EOF"
    value = p.value if p else "EOF"
    error = p.type if p else "EOF"
    print(f"[bold red]Error de sintaxis en linea {lineo} en el valor {value}[/bold red] {error}")
    
    