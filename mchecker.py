from collections import ChainMap
from typing import Union
from myAST import *

class SymbolTable:
    def __init__(self):
        # Utilizamos ChainMap para gestionar múltiples niveles de alcance
        self.scopes = ChainMap()

    def enter_scope(self):
        # Añadir un nuevo alcance
        self.scopes = self.scopes.new_child()

    def exit_scope(self):
        # Salir del alcance actual
        self.scopes = self.scopes.parents

    def declare(self, name: str, symbol):
        # Declara un símbolo en el alcance actual
        if name in self.scopes:
            raise ValueError(f"Error: '{name}' ya está declarado en este alcance.")
        self.scopes[name] = symbol

    def lookup(self, name: str):
        # Busca un símbolo en los alcances actuales
        return self.scopes.get(name, None)


class SemanticAnalyzer(Visitor):
    def __init__(self):
        self.symbol_table = SymbolTable()

    def visit(self, node: Node):
        # Redirige a métodos específicos de cada tipo de nodo en el AST
        method_name = 'visit_' + node.__class__.__name__
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node: Node):
        for field in getattr(node, '__dataclass_fields__', []):
            value = getattr(node, field)
            if isinstance(value, Node):
                self.visit(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, Node):
                        self.visit(item)

    def visit_Program(self, node: Program):
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_ClassDecl(self, node: ClassDecl):
        # Registrar la clase en la tabla de símbolos
        self.symbol_table.declare(node.ident, node)
        self.symbol_table.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.symbol_table.exit_scope()

    def visit_FuncDecl(self, node: FuncDecl):
        # Registrar la función en la tabla de símbolos
        self.symbol_table.declare(node.ident, node)
        self.symbol_table.enter_scope()
        for param in node.params:
            self.visit(param)
        for stmt in node.body:
            self.visit(stmt)
        self.symbol_table.exit_scope()

    def visit_VarDecl(self, node: VarDecl):
        if not self.symbol_table.lookup(node.ident):
            self.symbol_table.declare(node.ident, node)
        else:
            raise ValueError(f"Error: La variable '{node.ident}' ya fue declarada.")

    def visit_ArrayDecl(self, node: ArrayDecl):
        if not self.symbol_table.lookup(node.ident):
            self.symbol_table.declare(node.ident, node)
            self.visit(node.size)
        else:
            raise ValueError(f"Error: El arreglo '{node.ident}' ya fue declarado.")

    def visit_ObjectDecl(self, node: ObjectDecl):
        if not self.symbol_table.lookup(node.instance_name):
            self.symbol_table.declare(node.instance_name, node)
            for arg in node.args:
                self.visit(arg)
        else:
            raise ValueError(f"Error: El objeto '{node.instance_name}' ya fue declarado.")

    def visit_ExprStmt(self, node: ExprStmt):
        self.visit(node.expr)

    def visit_NullStmt(self, node: NullStmt):
        pass  # No necesita validación adicional

    def visit_IfStmt(self, node: IfStmt):
      # Visitar la condición del "if"
      self.visit(node.cond)
      
      # Crear un nuevo alcance para el bloque "then"
      self.symbol_table.enter_scope()
      for stmt in node.then_stmt:
          self.visit(stmt)
      self.symbol_table.exit_scope()
      
      # Manejo del bloque "else" si está presente
      if node.else_stmt:
          self.symbol_table.enter_scope()
          # Verificar si `else_stmt` es una lista o un solo nodo
          if isinstance(node.else_stmt, list):
              for stmt in node.else_stmt:
                  self.visit(stmt)
          else:
              self.visit(node.else_stmt)  # Si es un solo nodo
          self.symbol_table.exit_scope()


    def visit_ReturnStmt(self, node: ReturnStmt):
        if node.expr:
            self.visit(node.expr)

    def visit_BreakStmt(self, node: BreakStmt):
        pass  # No necesita validación adicional para declaración

    def visit_ContinueStmt(self, node: ContinueStmt):
        pass  # No necesita validación adicional para declaración

    def visit_WhileStmt(self, node: WhileStmt):
        self.visit(node.cond)
        self.symbol_table.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.symbol_table.exit_scope()

    def visit_ForStmt(self, node: ForStmt):
        self.symbol_table.enter_scope()
        self.visit(node.var_increment)
        self.visit(node.cond)
        self.visit(node.increment)
        for stmt in node.body:
            self.visit(stmt)
        self.symbol_table.exit_scope()

    def visit_PrintStmt(self, node: PrintStmt):
        self.visit(node.expr)

    def visit_SizeStmt(self, node: SizeStmt):
        if not self.symbol_table.lookup(node.ident):
            raise ValueError(f"Error: La variable o arreglo '{node.ident}' no ha sido declarada.")

    def visit_ThisStmt(self, node: ThisStmt):
        # Validación para asegurar que `this` se use dentro de un contexto de clase, si es aplicable
        pass  # Implementar según las reglas de uso de `this`

    def visit_SuperStmt(self, node: SuperStmt):
        for arg in node.args_list:
            self.visit(arg)

    def visit_PrivateStmt(self, node: PrivateStmt):
        pass  # No requiere validación en esta fase

    def visit_PublicStmt(self, node: PublicStmt):
        pass  # No requiere validación en esta fase

    def visit_CallExpr(self, node: CallExpr):
        if not self.symbol_table.lookup(node.ident):
            raise ValueError(f"Error: La función '{node.ident}' no ha sido declarada.")
        for arg in node.args:
            self.visit(arg)

    def visit_ConstExpr(self, node: ConstExpr):
        pass  # Constantes no requieren validación adicional

    def visit_VarExpr(self, node: VarExpr):
        if not self.symbol_table.lookup(node.ident):
            raise ValueError(f"Error: La variable '{node.ident}' no ha sido declarada.")

    def visit_ArrayLookupExpr(self, node: ArrayLookupExpr):
        if not self.symbol_table.lookup(node.ident):
            raise ValueError(f"Error: El arreglo '{node.ident}' no ha sido declarado.")
        self.visit(node.index)

    def visit_VarAssignExpr(self, node: VarAssignExpr):
        if not self.symbol_table.lookup(node.ident):
            raise ValueError(f"Error: La variable '{node.ident}' no ha sido declarada.")
        self.visit(node.expr)

    def visit_ArrayAssignExpr(self, node: ArrayAssignExpr):
        if not self.symbol_table.lookup(node.ident):
            raise ValueError(f"Error: El arreglo '{node.ident}' no ha sido declarado.")
        self.visit(node.index)
        self.visit(node.expr)

    def visit_ArraySizeExpr(self, node: ArraySizeExpr):
        if not self.symbol_table.lookup(node.ident):
            raise ValueError(f"Error: El arreglo '{node.ident}' no ha sido declarado.")

    def visit_BinaryExpr(self, node: BinaryExpr):
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryExpr(self, node: UnaryExpr):
        self.visit(node.expr)

    def visit_GroupingExpr(self, node: GroupingExpr):
        self.visit(node.expr)

