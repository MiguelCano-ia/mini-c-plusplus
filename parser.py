from dataclasses import dataclass
import sly
from lexer import Lexer
from myAST import *

class Parser(sly.Parser):
    # Nombre del archivo de depuración generado por SLY
    debugfile = 'parser.out'
    
    # Importamos los tokens desde el lexer
    tokens = Lexer.tokens

    precedence = (
      ('right', 'INCREMENT', 'DECREMENT'), 
      ('right', 'CAST'),
      ('nonassoc', IFX),
      ('nonassoc', ELSE),
      ('right', '!', 'NOT', '+', '-'),
      ('left', 'PLUS_ASSIGN', 'MINUS_ASSIGN', 'MULT_ASSIGN', 'DIV_ASSIGN'),
    ) 

    def __init__(self):
        self.debugging = True

    # Reglas de gramática
    
    # Programa inicial: lista de declaraciones
    @_("decl_list")
    def program(self, p):
        return Program(p.decl_list)

    @_("decl_list decl")
    def decl_list(self, p):
        return p.decl_list + [p.decl]

    @_("decl")
    def decl_list(self, p):
        return [p.decl]

    # Declaraciones: variables, funciones, clases y objetos
    @_("var_decl", "func_decl", "class_decl", "object_decl")
    def decl(self, p):
        return p[0]

    # Declaración de clase
    @_("CLASS IDENT '{' class_body '}' ';'")
    def class_decl(self, p):
        return ClassDecl(p.IDENT, None, p.class_body)
      
    @_("CLASS IDENT ':' IDENT '{' class_body '}' ';'")
    def class_decl(self, p):
        return ClassDecl(p.IDENT0, p.IDENT1, p.class_body)

    @_("access_specifier class_body")
    def class_body(self, p):
        return p.class_body

    @_("class_member class_body")
    def class_body(self, p):
        return [p.class_member] + p.class_body

    @_("empty")
    def class_body(self, p):
        return []

    @_("PRIVATE ':'", "PUBLIC ':'")
    def access_specifier(self, p):
        return p[0]

    @_("var_decl", "method_decl", "constructor_decl")
    def class_member(self, p):
        return p[0]

    @_("type_spec IDENT '(' param_list ')' compound_stmt")
    def method_decl(self, p):
        return FuncDecl(p.type_spec, p.IDENT, p.param_list, p.compound_stmt)

    @_("IDENT '(' param_list ')' compound_stmt")
    def constructor_decl(self, p):
        return FuncDecl(None, p.IDENT, p.param_list, p.compound_stmt)

    # Declaración de función
    @_("type_spec IDENT '(' param_list ')' compound_stmt")
    def func_decl(self, p):
        return FuncDecl(p.type_spec, p.IDENT, p.param_list, p.compound_stmt)

    # Lista de parámetros
    @_("empty")
    def param_list(self, p):
        return []

    @_("param_list ',' param")
    def param_list(self, p):
        return p.param_list + [p.param]

    @_("param")
    def param_list(self, p):
        return [p.param]

    @_("type_spec IDENT")
    def param(self, p):
        return VarDecl(p.type_spec, p.IDENT)

    @_("type_spec IDENT '[' INTLIT ']'")
    def param(self, p):
        return ArrayDecl(ident=p.IDENT, var_type=p.type_spec, size=p.INTLIT)

    # Sentencia compuesta (bloque de código)
    @_("'{' block_items '}'")
    def compound_stmt(self, p):
        return p.block_items
      
    @_("block_items block_item")
    def block_items(self, p):
        return p.block_items + [p.block_item]
      
    @_("block_item")
    def block_items(self, p):
        return [p.block_item]
      
    @_("stmt", "var_decl")
    def block_item(self, p):
        return p[0]
  
    # Sentencias posibles
    @_("expr_stmt", "compound_stmt", "if_stmt", "return_stmt", "while_stmt",
       "break_stmt", "continue_stmt", "super_stmt",
       "object_decl", "for_stmt", "this_stmt", "printf_stmt", "sprintf_stmt")
    def stmt(self, p):
        return p[0]
      
    @_("PRINTF '(' STRINGLIT ',' args_list ')' ';'")
    def printf_stmt(self, p):
        return PrintStmt(p.STRINGLIT, p.args_list)
      
    @_("PRINTF '(' STRINGLIT ')' ';'")
    def printf_stmt(self, p):
        return PrintStmt(p.STRINGLIT, [])
      
    @_("SPRINTF '(' expr ',' STRINGLIT ',' args_list ')' ';'")
    def sprintf_stmt(self, p):
        return SPrintStmt(p.expr, p.STRINGLIT, p.args_list)
    
    @_("SPRINTF '(' expr ',' STRINGLIT ')' ';'")
    def sprintf_stmt(self, p):
        return SPrintStmt(p.expr, p.STRINGLIT, [])


    # Sentencia 'for'
    @_("FOR '(' for_init ';' for_cond ';' for_incr ')' compound_stmt")
    def for_stmt(self, p):
        return ForStmt(
            initialization=p.for_init,
            condition=p.for_cond,
            increment=p.for_incr,
            body=p.compound_stmt
        )

    # Ajuste en 'for_init' para usar 'var_decl_no_semi'
    @_("var_decl_no_semi")
    def for_init(self, p):
        return p.var_decl_no_semi

    @_("assignment_expr")
    def for_init(self, p):
        return p.assignment_expr
      
    @_("empty")
    def for_init(self, p):
        return None

    # Declaraciones de variables sin punto y coma
    @_("type_spec IDENT")
    def var_decl_no_semi(self, p):
        return VarDecl(p.type_spec, p.IDENT)

    @_("type_spec IDENT '=' assignment_expr")
    def var_decl_no_semi(self, p):
        return VarDecl(p.type_spec, p.IDENT, p.assignment_expr)
      

    @_("type_spec IDENT '[' expr ']'")
    def var_decl_no_semi(self, p):
        return ArrayDecl(p.type_spec, p.IDENT, p.expr)

    @_("expr")
    def for_cond(self, p):
        return p.expr

    @_("empty")
    def for_cond(self, p):
        return None

    # Ajuste en 'for_incr' si es necesario
    @_("assignment_expr")
    def for_incr(self, p):
        return p.assignment_expr

    @_("empty")
    def for_incr(self, p):
        return None

    # Sentencia 'super'
    @_("SUPER '(' args_list ')' ';'")
    def super_stmt(self, p):  
        return SuperStmt(p.args_list)

    # Sentencia de expresión
    @_("assignment_expr ';'")
    def expr_stmt(self, p):
        return ExprStmt(p.assignment_expr)
      

    # Expresiones de asignación
    @_("IDENT '=' assignment_expr",
       "IDENT PLUS_ASSIGN assignment_expr",
       "IDENT MINUS_ASSIGN assignment_expr",
       "IDENT MULT_ASSIGN assignment_expr",
       "IDENT DIV_ASSIGN assignment_expr")
    def assignment_expr(self, p):
        if p[1] == '=':
            return VarAssignExpr(p.IDENT, p.assignment_expr)
        else:
            return CompoundAssignExpr(ident=p.IDENT, operator=p[1], expr=p.assignment_expr)

    @_("expr")
    def assignment_expr(self, p):
        return p.expr
      
    @_("NULL")
    def primary_expr(self, p):
        return NullExpr() 
      
    @_("IDENT '[' expr ']' '=' assignment_expr")
    def assignment_expr(self, p):
        return ArrayAssignExpr(p.IDENT, p.expr, p.assignment_expr)
      
    # Sentencia 'if'
    @_("IF '(' expr ')' stmt %prec IFX")
    def if_stmt(self, p):
        return IfStmt(cond=p.expr, then_stmt=p.stmt)

    @_("IF '(' expr ')' stmt ELSE stmt")
    def if_stmt(self, p):
        return IfStmt(cond=p.expr, then_stmt=p.stmt0, else_stmt=p.stmt1)

    # Sentencia 'return'
    @_("RETURN ';'")
    def return_stmt(self, p):
        return ReturnStmt()

    @_("RETURN expr ';'")
    def return_stmt(self, p):
        return ReturnStmt(p.expr)

    # Sentencia 'while'
    @_("WHILE '(' expr ')' stmt")
    def while_stmt(self, p):
        return WhileStmt(cond=p.expr, body=p.stmt)

    # Sentencias 'break' y 'continue'
    @_("BREAK ';'")
    def break_stmt(self, p):
        return BreakStmt()

    @_("CONTINUE ';'")
    def continue_stmt(self, p):
        return ContinueStmt()

    # Lista de argumentos
    @_("empty")
    def args_list(self, p):
        return []

    @_("args_list ',' expr")
    def args_list(self, p):
        return p.args_list + [p.expr]

    @_("expr")
    def args_list(self, p):
        return [p.expr]

    # Sentencia 'printf'
      
    # Sentencia 'this'
    @_("THIS ';'")
    def this_stmt(self, p):
        return ThisStmt()

    # Declaración de variables
    @_("type_spec IDENT ';'")
    def var_decl(self, p):
        return VarDecl(p.type_spec, p.IDENT)

    @_("type_spec IDENT '=' assignment_expr ';'")
    def var_decl(self, p):
        return VarDecl(p.type_spec, p.IDENT, p.assignment_expr)
      
    

    @_("type_spec IDENT '[' expr ']' ';'")
    def var_decl(self, p):
        return ArrayDecl(p.type_spec, p.IDENT, p.expr)

    # Declaración de objetos
    @_("IDENT IDENT ';'")
    def object_decl(self, p):
        return ObjectDecl(class_type=p.IDENT0, instance_name=p.IDENT1, args=None)

    @_("IDENT IDENT '=' NEW IDENT '(' args_list ')' ';'")
    def object_decl(self, p):
        return ObjectDecl(class_type=p.IDENT0, instance_name=p.IDENT1, args=p.args_list)

    # Especificadores de tipo
    @_("VOID", "INT", "FLOAT", "BOOL", "STRING")
    def type_spec(self, p):
        return p[0]

    # Definición de expresiones con precedencia explícita

    @_("logical_or_expr")
    def expr(self, p):
        return p.logical_or_expr

    # Operadores lógicos 'OR'
    @_("logical_or_expr OR logical_and_expr")
    def logical_or_expr(self, p):
        return ShortCircuitOrExpr(p.logical_or_expr, p.logical_and_expr)

    @_("logical_and_expr")
    def logical_or_expr(self, p):
        return p.logical_and_expr

    # Operadores lógicos 'AND'
    @_("logical_and_expr AND equality_expr")
    def logical_and_expr(self, p):
        return ShortCircuitAndExpr(p.logical_and_expr, p.equality_expr)

    @_("equality_expr")
    def logical_and_expr(self, p):
        return p.equality_expr

    # Operadores de igualdad '==' y '!='
    @_("equality_expr EQ relational_expr",
       "equality_expr NE relational_expr")
    def equality_expr(self, p):
        return BinaryExpr(p.equality_expr, p[1], p.relational_expr)

    @_("relational_expr")
    def equality_expr(self, p):
        return p.relational_expr

    # Operadores relacionales '<', '<=', '>', '>='
    @_("relational_expr LT additive_expr",
       "relational_expr LE additive_expr",
       "relational_expr GT additive_expr",
       "relational_expr GE additive_expr")
    def relational_expr(self, p):
        return BinaryExpr(p.relational_expr, p[1], p.additive_expr)

    @_("additive_expr")
    def relational_expr(self, p):
        return p.additive_expr

    # Operadores aditivos '+' y '-'
    @_("additive_expr '+' multiplicative_expr",
       "additive_expr '-' multiplicative_expr")
    def additive_expr(self, p):
        return BinaryExpr(p.additive_expr, p[1], p.multiplicative_expr)

    @_("multiplicative_expr")
    def additive_expr(self, p):
        return p.multiplicative_expr

    # Operadores multiplicativos '*', '/', '%'
    @_("multiplicative_expr '*' unary_expr",
       "multiplicative_expr '/' unary_expr",
       "multiplicative_expr '%' unary_expr")
    def multiplicative_expr(self, p):
        return BinaryExpr(p.multiplicative_expr, p[1], p.unary_expr)

    @_("unary_expr")
    def multiplicative_expr(self, p):
        return p.unary_expr

    @_('INCREMENT unary_expr',
       'DECREMENT unary_expr',
       "'+' unary_expr",
       "'-' unary_expr",
       "'!' unary_expr",
       "NOT unary_expr")
    def unary_expr(self, p):
        if p[0] == '++':
            return PrefixIncExpr(p.unary_expr)
        elif p[0] == '--':
            return PrefixDecExpr(p.unary_expr)
        else:
            return UnaryExpr(p[0], p.unary_expr)

    @_("postfix_expr")
    def unary_expr(self, p):
        return p.postfix_expr

    # Expresiones postfijas
    @_('postfix_expr INCREMENT',
       'postfix_expr DECREMENT')
    def postfix_expr(self, p):
        if p[1] == '++':
            return PostfixIncExpr(p.postfix_expr)
        elif p[1] == '--':
            return PostfixDecExpr(p.postfix_expr)

    @_('primary_expr')
    def postfix_expr(self, p):
        return p.primary_expr

    
    @_("'(' type_spec ')' unary_expr %prec CAST")
    def unary_expr(self, p):
        return CastExpr(p.type_spec, p.unary_expr)

    # Expresiones primarias
    @_("'(' expr ')'")
    def primary_expr(self, p):
        return GroupingExpr(p.expr)

    @_("INTLIT", "FLOATLIT", "BOOLIT", "STRINGLIT", "TRUE", "FALSE")
    def primary_expr(self, p):
        return ConstExpr(p[0])

    @_("IDENT '(' args_list ')'")
    def primary_expr(self, p):
        return CallExpr(p.IDENT, p.args_list)

    @_("IDENT '.' IDENT '(' args_list ')'")
    def primary_expr(self, p):
        return CallExpr(object_name=p.IDENT0, ident=p.IDENT1, args=p.args_list)

    @_("IDENT '[' expr ']'")
    def primary_expr(self, p):
        return ArrayLookupExpr(p.IDENT, p.expr)

    @_("IDENT")
    def primary_expr(self, p):
        return VarExpr(p.IDENT)

    # Expresión para obtener el tamaño de un arreglo
    @_("IDENT '.' SIZE")
    def primary_expr(self, p):
        return ArraySizeExpr(p.IDENT)

    # Regla para una producción vacía
    @_("")
    def empty(self, p):
        pass  # No se devuelve nada

    # Manejo de errores de sintaxis
    def error(self, p):
        if p:
            lineo = p.lineno
            value = p.value
            error_type = p.type
            print(f"[bold red]Error de sintaxis en línea {lineo} en el valor '{value}' ({error_type})[/bold red]")
        else:
            print("[bold red]Error de sintaxis: fin de archivo inesperado[/bold red]")
