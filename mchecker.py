from collections import ChainMap
from typing import List, Union
from myAST import *

class SemanticAnalyzer(Visitor):
    def __init__(self):
        self.symtable = ChainMap()
        self.errors = []
        self.current_function = None
        self.current_class = None
        self.loop_nesting = 0  # Para controlar 'break' y 'continue'x
        self.functions_declared = {}  # Nuevo atributo para las funciones declaradas

    def visit(self, node):
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        print(f"No hay método visit_{node.__class__.__name__}")

    def lookup(self, name):
        for scope in self.symtable.maps:
            if name in scope:
                return scope[name]
        return None

    def lookup_class(self, class_name):
        for scope in self.symtable.maps:
            if class_name in scope:
                class_decl = scope[class_name]
                if isinstance(class_decl, ClassDecl):
                    return class_decl
        return None

    def find_constructor(self, class_decl, class_name):
        for member in class_decl.body:
            if isinstance(member, FuncDecl) and member.ident == class_name:
                return member
        return None

    def find_method(self, class_decl, method_name):
        for member in class_decl.body:
            if isinstance(member, FuncDecl) and member.ident == method_name:
                return member
        if class_decl.super_class:
            super_class_decl = self.lookup_class(class_decl.super_class)
            if super_class_decl:
                return self.find_method(super_class_decl, method_name)
        return None

    def check_assignment_compatibility(self, var_type, expr_type):
        if var_type == expr_type:
            return True
        if var_type == 'float' and expr_type == 'int':
            return True
        return False

    def check_binary_operation(self, operator, left_type, right_type):
        numeric_ops = {'+', '-', '*', '/', '%'}
        relational_ops = {'<', '<=', '>', '>=', '==', '!='}
        logical_ops = {'AND', 'OR', '&&', '||', '!'}
        if operator in numeric_ops:
            if left_type == 'int' and right_type == 'int':
                return 'int'
            elif left_type in {'int', 'float'} and right_type in {'int', 'float'}:
                return 'float'
            else:
                return None
        elif operator in relational_ops:
            if left_type in {'int', 'float'} and right_type in {'int', 'float'}:
                return 'bool'
            else:
                return None
        elif operator in logical_ops:
            if left_type == 'bool' and right_type == 'bool':
                return 'bool'
            else:
                return None
        else:
            return None

    def check_unary_operation(self, operator, expr_type):
        if operator == '!':
            if expr_type == 'bool':
                return 'bool'
            else:
                return None
        elif operator in {'+', '-'}:
            if expr_type in {'int', 'float'}:
                return expr_type
            else:
                return None
        elif operator in {'++', '--'}:
            if expr_type in {'int', 'float'}:
                return expr_type
            else:
                return None
        else:
            return None
        
    def check_main_function(self):
        main_func = self.functions_declared.get('main')
        if main_func is None:
            self.errors.append("Error: No se encontró la función 'main' en el programa.")
        else:
            if main_func.return_type != 'int':
                self.errors.append("Error: La función 'main' debe tener tipo de retorno 'int'.")
            if len(main_func.params) != 0:
                self.errors.append("Error: La función 'main' no debe tener parámetros.")
                
    def is_cast_valid(self, from_type: str, to_type: str) -> bool:
        valid_casts = {
            'int': ['float'],
            'float': ['int'],
        }
        return to_type in valid_casts.get(from_type, []) or from_type == to_type

    # Implementación de los métodos visit_ para cada nodo del AST

    def visit_Program(self, node: Program):
        for stmt in node.stmts:
            self.visit(stmt)
        # Verificar la función 'main' al final del análisis
        self.check_main_function()


    def visit_FuncDecl(self, node: FuncDecl):
        func_name = node.ident

        if func_name in self.symtable.maps[0]:
            self.errors.append(f"Error: Función '{func_name}' ya declarada.")
            return
        else:
            self.symtable[func_name] = node  

        self.functions_declared[func_name] = node

        self.current_function = node
        self.symtable = self.symtable.new_child()

        for param in node.params:
            if param.ident in self.symtable.maps[0]:
                self.errors.append(f"Error: Parámetro '{param.ident}' ya declarado en la función '{func_name}'.")
            else:
                self.symtable[param.ident] = param.var_type

        for stmt in node.body:
            self.visit(stmt)

        self.symtable = self.symtable.parents
        self.current_function = None


    def visit_VarDecl(self, node: VarDecl):
        var_name = node.ident
        if var_name in self.symtable.maps[0]:
            self.errors.append(f"Error: Variable '{var_name}' ya declarada en este ámbito.")
        else:
            self.symtable[var_name] = node.var_type
        if node.expr:
            expr_type = self.visit(node.expr)
            if not self.check_assignment_compatibility(node.var_type, expr_type):
                self.errors.append(f"Error: No se puede asignar un valor de tipo '{expr_type}' a la variable '{var_name}' de tipo '{node.var_type}'.")

    def visit_ArrayDecl(self, node: ArrayDecl):
        array_name = node.ident
        if array_name in self.symtable.maps[0]:
            self.errors.append(f"Error: Arreglo '{array_name}' ya declarado en este ámbito.")
        else:
            self.symtable[array_name] = node
        size_type = self.visit(node.size)
        if size_type != 'int':
            self.errors.append(f"Error: El tamaño del arreglo '{array_name}' debe ser un entero, se obtuvo '{size_type}'.")

    def visit_ObjectDecl(self, node: ObjectDecl):
        object_name = node.instance_name
        class_name = node.class_type
        if object_name in self.symtable.maps[0]:
            self.errors.append(f"Error: Objeto '{object_name}' ya declarado en este ámbito.")
        else:
            self.symtable[object_name] = class_name
        class_decl = self.lookup_class(class_name)
        if class_decl is None:
            self.errors.append(f"Error: Clase '{class_name}' no declarada.")
        else:
            if node.args:
                constructor = self.find_constructor(class_decl, class_name)
                if constructor:
                    if len(node.args) != len(constructor.params):
                        self.errors.append(f"Error: El constructor de '{class_name}' espera {len(constructor.params)} argumentos, pero se proporcionaron {len(node.args)}.")
                    else:
                        for arg_expr, param in zip(node.args, constructor.params):
                            arg_type = self.visit(arg_expr)
                            param_type = param.var_type
                            if not self.check_assignment_compatibility(param_type, arg_type):
                                self.errors.append(f"Error: El argumento de tipo '{arg_type}' no es compatible con el parámetro '{param.ident}' de tipo '{param_type}' en el constructor de '{class_name}'.")
                else:
                    self.errors.append(f"Error: No se encontró un constructor para la clase '{class_name}'.")

    def visit_ExprStmt(self, node: ExprStmt):
        self.visit(node.expr)

    def visit_NullStmt(self, node: NullStmt):
        pass

    def visit_IfStmt(self, node: IfStmt):
        cond_type = self.visit(node.cond)
        if cond_type != 'bool':
            self.errors.append(f"Error: La condición del 'if' debe ser de tipo 'bool', se obtuvo '{cond_type}'.")
        self.symtable = self.symtable.new_child()
        for stmt in node.then_stmt:
            self.visit(stmt)
        self.symtable = self.symtable.parents
        if node.else_stmt:
            self.symtable = self.symtable.new_child()
            if isinstance(node.else_stmt, list):
                for stmt in node.else_stmt:
                    self.visit(stmt)
            else:
                self.visit(node.else_stmt)
            self.symtable = self.symtable.parents

    def visit_ReturnStmt(self, node: ReturnStmt):
        if self.current_function is None:
            self.errors.append("Error: 'return' fuera de una función.")
            return
        if node.expr:
            return_type = self.visit(node.expr)
        else:
            return_type = 'void'
        expected_type = self.current_function.return_type
        if return_type != expected_type:
            self.errors.append(f"Error: La función '{self.current_function.ident}' debe retornar '{expected_type}', pero retorna '{return_type}'.")

    def visit_BreakStmt(self, node: BreakStmt):
        if self.loop_nesting == 0:
            self.errors.append("Error: 'break' fuera de un bucle.")

    def visit_ContinueStmt(self, node: ContinueStmt):
        if self.loop_nesting == 0:
            self.errors.append("Error: 'continue' fuera de un bucle.")

    def visit_WhileStmt(self, node: WhileStmt):
        cond_type = self.visit(node.cond)
        if cond_type != 'bool':
            self.errors.append(f"Error: La condición del 'while' debe ser de tipo 'bool', se obtuvo '{cond_type}'.")
        self.loop_nesting += 1
        self.symtable = self.symtable.new_child()
        for stmt in node.body:
            self.visit(stmt)
        self.symtable = self.symtable.parents
        self.loop_nesting -= 1

    def visit_ForStmt(self, node: ForStmt):
        self.loop_nesting += 1
        self.symtable = self.symtable.new_child()

        if node.initialization:
            self.visit(node.initialization)

        if node.condition:
            cond_type = self.visit(node.condition)
            if cond_type != 'bool':
                self.errors.append(f"Error: La condición del 'for' debe ser de tipo 'bool', se obtuvo '{cond_type}'.")
        else:
            pass
        if node.increment:
            self.visit(node.increment)

        for stmt in node.body:
            self.visit(stmt)

        self.symtable = self.symtable.parents
        self.loop_nesting -= 1


    def visit_PrintStmt(self, node: PrintStmt):
        self.visit(node.expr)

    def visit_SizeStmt(self, node: SizeStmt):
        var_type = self.lookup(node.ident)
        if var_type is None:
            self.errors.append(f"Error: Variable '{node.ident}' no declarada.")
        elif not isinstance(var_type, ArrayDecl):
            self.errors.append(f"Error: '{node.ident}' no es un arreglo.")
        return 'int'

    def visit_ThisStmt(self, node: ThisStmt):
        if self.current_class is None:
            self.errors.append("Error: 'this' fuera de una clase.")
        else:
            return self.current_class.ident

    def visit_SuperStmt(self, node: SuperStmt):
        if self.current_class is None:
            self.errors.append("Error: 'super' fuera de una clase.")
            return
        if self.current_class.super_class is None:
            self.errors.append(f"Error: La clase '{self.current_class.ident}' no tiene superclase.")
            return
        super_class = self.lookup_class(self.current_class.super_class)
        if super_class is None:
            self.errors.append(f"Error: Superclase '{self.current_class.super_class}' no declarada.")
            return
        constructor = self.find_constructor(super_class, super_class.ident)
        if constructor:
            if len(node.args_list) != len(constructor.params):
                self.errors.append(f"Error: El constructor de '{super_class.ident}' espera {len(constructor.params)} argumentos, pero se proporcionaron {len(node.args_list)}.")
            else:
                for arg_expr, param in zip(node.args_list, constructor.params):
                    arg_type = self.visit(arg_expr)
                    param_type = param.var_type
                    if not self.check_assignment_compatibility(param_type, arg_type):
                        self.errors.append(f"Error: El argumento de tipo '{arg_type}' no es compatible con el parámetro '{param.ident}' de tipo '{param_type}' en el constructor de '{super_class.ident}'.")
        else:
            self.errors.append(f"Error: No se encontró un constructor para la clase '{super_class.ident}'.")

    def visit_PrivateStmt(self, node: PrivateStmt):
        pass

    def visit_PublicStmt(self, node: PublicStmt):
        pass

    def visit_CallExpr(self, node: CallExpr):
        if node.object_name:
            object_type = self.lookup(node.object_name)
            if object_type is None:
                self.errors.append(f"Error: Objeto '{node.object_name}' no declarado.")
                return None
            class_decl = self.lookup_class(object_type)
            if class_decl is None:
                self.errors.append(f"Error: Tipo de objeto '{object_type}' no es una clase válida.")
                return None
            method_decl = self.find_method(class_decl, node.ident)
            if method_decl is None:
                self.errors.append(f"Error: Método '{node.ident}' no encontrado en la clase '{object_type}'.")
                return None
            if len(node.args) != len(method_decl.params):
                self.errors.append(f"Error: El método '{node.ident}' de la clase '{object_type}' espera {len(method_decl.params)} argumentos, pero se proporcionaron {len(node.args)}.")
            else:
                for arg_expr, param in zip(node.args, method_decl.params):
                    arg_type = self.visit(arg_expr)
                    param_type = param.var_type
                    if not self.check_assignment_compatibility(param_type, arg_type):
                        self.errors.append(f"Error: El argumento de tipo '{arg_type}' no es compatible con el parámetro '{param.ident}' de tipo '{param_type}' en el método '{node.ident}' de la clase '{object_type}'.")
            return method_decl.return_type
        else:
            func_decl = self.lookup(node.ident)
            if func_decl is None or not isinstance(func_decl, FuncDecl):
                self.errors.append(f"Error: Función '{node.ident}' no declarada.")
                return None
            if len(node.args) != len(func_decl.params):
                self.errors.append(f"Error: La función '{node.ident}' espera {len(func_decl.params)} argumentos, pero se proporcionaron {len(node.args)}.")
            else:
                for arg_expr, param in zip(node.args, func_decl.params):
                    arg_type = self.visit(arg_expr)
                    param_type = param.var_type
                    if not self.check_assignment_compatibility(param_type, arg_type):
                        self.errors.append(f"Error: El argumento de tipo '{arg_type}' no es compatible con el parámetro '{param.ident}' de tipo '{param_type}' en la función '{node.ident}'.")
            return func_decl.return_type

    def visit_ConstExpr(self, node: ConstExpr):
        if isinstance(node.value, bool):
            return 'bool'
        elif node.value in {'TRUE', 'FALSE'}:
            return 'bool'
        elif isinstance(node.value, int):
            return 'int'
        elif isinstance(node.value, float):
            return 'float'
        elif isinstance(node.value, str):
            return 'string'
        else:
            self.errors.append(f"Error: Tipo de constante desconocido '{node.value}'.")
            return None

    def visit_VarExpr(self, node: VarExpr):
        var_type = self.lookup(node.ident)
        if var_type is None:
            self.errors.append(f"Error: Variable '{node.ident}' no declarada.")
            return None
        return var_type

    def visit_ArrayLookupExpr(self, node: ArrayLookupExpr):
        array_decl = self.lookup(node.ident)
        if array_decl is None:
            self.errors.append(f"Error: Arreglo '{node.ident}' no declarado.")
            return None
        if not isinstance(array_decl, ArrayDecl):
            self.errors.append(f"Error: '{node.ident}' no es un arreglo.")
            return None
        index_type = self.visit(node.index)
        if index_type != 'int':
            self.errors.append(f"Error: El índice del arreglo debe ser de tipo 'int', se obtuvo '{index_type}'.")
        return array_decl.var_type

    def visit_VarAssignExpr(self, node: VarAssignExpr):
        var_type = self.lookup(node.ident)
        if var_type is None:
            self.errors.append(f"Error: Variable '{node.ident}' no declarada.")
            return None
        expr_type = self.visit(node.expr)
        if not self.check_assignment_compatibility(var_type, expr_type):
            self.errors.append(
                f"Error: No se puede asignar un valor de tipo '{expr_type}' a la variable '{node.ident}' de tipo '{var_type}'."
            )
        return var_type

    def visit_ArrayAssignExpr(self, node: ArrayAssignExpr):
        array_decl = self.lookup(node.ident)
        if array_decl is None:
            self.errors.append(f"Error: Arreglo '{node.ident}' no declarado.")
            return None
        if not isinstance(array_decl, ArrayDecl):
            self.errors.append(f"Error: '{node.ident}' no es un arreglo.")
            return None
        index_type = self.visit(node.index)
        if index_type != 'int':
            self.errors.append(f"Error: El índice del arreglo debe ser de tipo 'int', se obtuvo '{index_type}'.")
        expr_type = self.visit(node.expr)
        elem_type = array_decl.var_type
        if not self.check_assignment_compatibility(elem_type, expr_type):
            self.errors.append(f"Error: No se puede asignar un valor de tipo '{expr_type}' al elemento del arreglo de tipo '{elem_type}'.")
        return elem_type

    def visit_ArraySizeExpr(self, node: ArraySizeExpr):
        array_decl = self.lookup(node.ident)
        if array_decl is None:
            self.errors.append(f"Error: Arreglo '{node.ident}' no declarado.")
            return None
        if not isinstance(array_decl, ArrayDecl):
            self.errors.append(f"Error: '{node.ident}' no es un arreglo.")
            return None
        return 'int'
    
    def visit_CompoundAssignExpr(self, node: CompoundAssignExpr):
        var_name = node.ident
        operator = node.operator
        expr = node.expr

        var_type = self.lookup(var_name)
        if var_type is None:
            self.errors.append(f"Error: Variable '{var_name}' no declarada.")
            return None

        expr_type = self.visit(expr)

        bin_operator = operator[0] 
        binary_expr = BinaryExpr(left=VarExpr(var_name), operand=bin_operator, right=expr)

        result_type = self.visit(binary_expr)

        if result_type is None:
            self.errors.append(f"Error: Operación '{operator}' no soportada entre '{var_type}' y '{expr_type}'.")
            return None

        if not self.check_assignment_compatibility(var_type, result_type):
            self.errors.append(f"Error: No se puede asignar un valor de tipo '{result_type}' a la variable '{var_name}' de tipo '{var_type}'.")
            return None

        return var_type

    def visit_BinaryExpr(self, node: BinaryExpr):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        result_type = self.check_binary_operation(node.operand, left_type, right_type)
        if result_type is None:
            self.errors.append(f"Error: Operación '{node.operand}' no soportada entre '{left_type}' y '{right_type}'.")
        return result_type

    def visit_UnaryExpr(self, node: UnaryExpr):
        expr_type = self.visit(node.expr)
        result_type = self.check_unary_operation(node.operand, expr_type)
        if result_type is None:
            self.errors.append(f"Error: Operación unaria '{node.operand}' no soportada para tipo '{expr_type}'.")
        return result_type
    
    def visit_CastExpr(self, node: CastExpr):
        expr_type = self.visit(node.expr)

        target_type = node.target_type

        if not self.is_cast_valid(expr_type, target_type):
            self.errors.append(f"No se puede convertir de {expr_type} a {target_type}")

        return target_type

    def visit_GroupingExpr(self, node: GroupingExpr):
        return self.visit(node.expr)

    def visit_IntToFloatExpr(self, node: IntToFloatExpr):
        expr_type = self.visit(node.expr)
        if expr_type != 'int':
            self.errors.append(f"Error: La conversión de 'int' a 'float' requiere un operando de tipo 'int', se obtuvo '{expr_type}'.")
        return 'float'

    def visit_ClassDecl(self, node: ClassDecl):
        class_name = node.ident
        if class_name in self.symtable.maps[0]:
            self.errors.append(f"Error: Clase '{class_name}' ya declarada en este ámbito.")
        else:
            self.symtable[class_name] = node
        self.current_class = node
        self.symtable = self.symtable.new_child()
        for member in node.body:
            self.visit(member)
        self.symtable = self.symtable.parents
        self.current_class = None

