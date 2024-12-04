from __future__ import annotations
import re 
from dataclasses import dataclass
from collections import ChainMap
from myAST import *
from multimethod import multimethod

@dataclass
class ScopeInfo:
    name: str      
    type: str      
    symbols: dict   

@dataclass
class SemanticAnalyzer(Visitor):
  symtable = ChainMap()
  all_scopes = [] 
  errors = []
  currentFunction = None
  currentClass = None
  loopNesting = 0
  functionsDeclared = {}
  
  def visit (self, node):
    methodName = 'visit' + node.__class__.__name__
    visitor = getattr(self, methodName, self.generic_visit)
    return visitor(node)
  
  def generic_visit(self, node):
    raise Exception(f"No visit method for {node.__class__.__name__}")

  def lookup(self, name):
    for scope in self.symtable.maps:
      if name in scope:
        return scope[name]
    return None

  def lookupClass(self, class_name):
    for scope in self.symtable.maps:
      if class_name in scope:
        class_decl = scope[class_name]
        if isinstance(class_decl, ClassDecl):
          return class_decl
    return None
  
  def enter_scope(self, name='Unnamed', scope_type='Bloque'):
    self.symtable = self.symtable.new_child()
    scope_info = ScopeInfo(name=name, type=scope_type, symbols=self.symtable.maps[0])
    self.all_scopes.append(scope_info)

  def leave_scope(self):
      self.symtable = self.symtable.parents
  
  def validateSuperClass(self, class_name, super_class_name):
    if super_class_name == class_name:
      self.errors.append(f"Error: Class '{class_name}' cannot inherit from itself")
      return None
    
    super_class = self.lookupClass(super_class_name)
    
    if super_class is None:
      self.errors.append(f"Error: Superclass '{super_class_name}' not declared")
      return None
    
    if super_class.super_class == class_name:
      self.errors.append(f"Error: Circular inheritance between '{class_name}' and '{super_class_name}'")
      return None
    
    return super_class 

  def findConstructor(self, class_decl, class_name):
    for member in class_decl.body:
      if isinstance(member, FuncDecl) and member.ident == class_name:
        return member
    return None

  def find_method(self, class_decl, method_name):
    for member in class_decl.body:
      if isinstance(member, FuncDecl) and member.ident == method_name:
        return member
      if class_decl.super_class:
        super_class_decl = self.lookupClass(class_decl.super_class)
        if super_class_decl:
          return self.find_method(super_class_decl, method_name)
    return None

  def checkAssignmentCompatibility(self, var_type, expr_type):
    if var_type == expr_type:
      return True
    if expr_type == 'null':
      if var_type == 'string':
        return True
      if var_type in self.symtable.maps[0]:
        class_decl = self.lookupClass(var_type)
        if class_decl:
          return True
    if var_type == 'int' and expr_type == 'float':
      return True
    return False

  def checkBinaryOperation(self, operator, leftType, rightType):
    numericOps = {'+', '-', '*', '/', '%'}
    relationalOps = {'<', '>', '<=', '>=', '==', '!='}
    equalityOps = {'==', '!='}
    logicalOps = {'AND', 'OR', '&&', '||', '!'}
    
    if operator in equalityOps:
      if leftType == 'null' or rightType == 'null':
        if leftType in self.symtable.maps[0] or rightType in self.symtable.maps[0]:
          return 'bool'
        if leftType == 'string' or rightType == 'string':
          return 'bool'
        self.errors.append(f"Error: Invalid comparison between '{leftType}' and '{rightType}'")
        return None
    if operator in numericOps:
      if leftType == 'int' and rightType == 'int':
        return 'int'
      elif leftType in {'int', 'float'} and rightType in {'int', 'float'}:
        return 'float'
      else:
        return None
    elif operator in relationalOps:
      if leftType in {'int', 'float'} and rightType in {'int', 'float'}:
        return 'bool'
      else:
        return None
    elif operator in logicalOps:
      if leftType == 'bool' and rightType == 'bool':
        return 'bool'
      else:
        return None
    else:
      return None

  def checkUnaryOperation(self, operator, exprType):
    if operator == '!':
      if exprType == 'bool':
        return 'bool'
      else:
        return None
    elif operator in {'+', '-'}:
      if exprType in {'int', 'float'}:
        return exprType
      else:
        return None
    elif operator in {'++', '--'}:
      if exprType in {'int', 'float'}:
        return exprType
      else:
        return None
    else:
      return None

  def checkMainFunction(self):
    mainFunc = self.functionsDeclared.get('main')
    if mainFunc is None:
      self.errors.append(f"Error: main function not declared")
    else:
      if mainFunc.return_type != 'int':
        self.errors.append(f"Error: main function must return int")
      if len(mainFunc.params) > 0:
        self.errors.append(f"Error: main function must not have parameters")

  def isCastValid(self, fromType: str, toType: str) -> bool:
    validCasts = {
      'int': [float],
      'float': [int],
    }
    return toType in validCasts.get(fromType, []) or fromType == toType

  # Visit methods

  @multimethod
  def visit(self, node: Program):
      self.symtable = ChainMap()
      self.all_scopes = [] 
      self.errors = []
      self.functionsDeclared = {}  
      self.currentFunction = None
      self.currentClass = None
      self.loopNesting = 0
      # Entrar en el scope global
      self.enter_scope(name='Global', scope_type='Global')
      
      for stmt in node.stmts:
          self.visit(stmt)
      
      # Verificar si la función main está declarada
      self.checkMainFunction()
      
      # Salir del scope global
      self.leave_scope()

  @multimethod
  def visit(self, node: FuncDecl):
    funcName = node.ident
    
    # Verificar si estamos dentro de una clase
    if self.currentClass is not None:
      className = self.currentClass.ident
      if funcName == className:
        # Es un constructor
        self.visitConstructor(node)
        return

    # Verificar si la función ya está declarada en el scope global
    if funcName in self.symtable.maps[0]:
        self.errors.append(f"Error: Function {funcName} already declared")
        return
    else:
        # Agregar la función a la tabla de símbolos global
        self.symtable.maps[0][funcName] = node
        self.functionsDeclared[funcName] = node

        # Establecer la función actual
        self.currentFunction = node

        # Entrar en un nuevo scope para la función
        self.enter_scope(name=funcName, scope_type='Función')

        # Agregar parámetros al scope actual
        for param in node.params:
            if param.ident in self.symtable.maps[0]:
                self.errors.append(f"Error: Parameter {param.ident} already declared in function {funcName}")
            else:
                self.symtable.maps[0][param.ident] = param.var_type

        # Visitar el cuerpo de la función
        for stmt in node.body:
            self.visit(stmt)

        # Salir del scope de la función
        self.leave_scope()
        self.currentFunction = None
        
  def visitConstructor(self, node: FuncDecl):
    constructorName = node.ident

    if constructorName in self.symtable.maps[0]:
        self.errors.append(f"Error: Constructor '{constructorName}' ya declarado en la clase '{self.currentClass.ident}'")
    else:
        self.symtable[constructorName] = {
            'kind': 'constructor',
            'params': node.params,
        }

    self.enter_scope(name=f"Constructor {constructorName}", scope_type='Constructor')

    for param in node.params:
        if param.ident in self.symtable.maps[0]:
            self.errors.append(f"Error: Parámetro '{param.ident}' ya declarado en el constructor '{constructorName}'")
        else:
            self.symtable[param.ident] = param.var_type 

    for stmt in node.body:
        self.visit(stmt)

    self.leave_scope()

        
  @multimethod
  def visit(self, node: NullExpr):
    return 'null'

  @multimethod
  def visit(self, node: VarDecl):
    varName = node.ident
    if varName in self.symtable.maps[0]:
      self.error.append(f"Error: Variable {varName} already declared")
    else:
      self.symtable[varName] = node.var_type
    if node.expr:
      exprType = self.visit(node.expr)
      if not self.checkAssignmentCompatibility(node.var_type, exprType):
        self.errors.append(f"Error: not able to assign {exprType} to variable {varName} of type {node.var_type}")

  @multimethod
  def visit(self, node: ArrayDecl):
    arrayName = node.ident
    if arrayName in self.symtable.maps[0]:
      self.errors.append(f"Error: Array {arrayName} already declared")
    else:
      self.symtable[arrayName] = node
    sizeType = self.visit(node.size)
    if sizeType != 'int':
      self.errors.append(f"Error: size of array {arrayName} must be of type int, found {sizeType}")

  @multimethod
  def visit(self, node: ObjectDecl):
    objectName = node.instance_name
    className = node.class_type
    if objectName in self.symtable.maps[0]:
      self.errors.append(f"Error: Object {objectName} already declared")
    else:
      self.symtable[objectName] = className
    classDecl = self.lookupClass(className)
    if classDecl is None:
      self.errors.append(f"Error: Class {className} not declared")
    else:
      if node.args:
        constructor = self.findConstructor(classDecl, className)
        if constructor:
          if len(node.args) != len(constructor.params):
            self.errors.append(f"Error: The constructor of the class {className} expects {len(constructor.params)} arguments, found {len(node.args)}")
          else:
            for argsExpr, param in zip(node.args, constructor.params):
              argType = self.visit(argsExpr)
              paramType = param.var_type
              if not self.checkAssignmentCompatibility(paramType, argType):
                self.errors.append(f"Error: Argument of type {argType} cannot be assigned to parameter of type {paramType}")
        else:
          self.errors.append(f"Error: Constructor for class {className} not found")

  @multimethod
  def visit(self, node: ExprStmt):
    self.visit(node.expr)

  @multimethod
  def visit(self, node: IfStmt):
    condType = self.visit(node.cond)
    if condType != 'bool':
      self.errors.append(f"Error: The 'if' condition must be of type 'bool', found '{condType}'")
      
    self.enter_scope(name='If-Then', scope_type='Bloque')
    for stmt in node.then_stmt:
      self.visit(stmt)
    self.leave_scope()
    
    if node.else_stmt:
      self.enter_scope(name='If-Else', scope_type='Bloque')
      if isinstance(node.else_stmt, list):
        for stmt in node.else_stmt:
          self.visit(stmt)
      else:
        self.visit(node.else_stmt)
      self.symtable = self.symtable.parents

  @multimethod
  def visit(self, node: ReturnStmt):
    if self.currentFunction is None:
      self.errors.append("Error: 'return' used outside a function")
      return
    if node.expr:
      returnType = self.visit(node.expr)
    else:
      returnType = 'void'
    expectedType = self.currentFunction.return_type
    if returnType != expectedType:
      self.errors.append(f"Error: Function '{self.currentFunction.ident}' should return '{expectedType}', but returns '{returnType}'")

  @multimethod
  def visit(self, node: BreakStmt):
    if self.loopNesting == 0:
      self.errors.append("Error: 'break' used outside of a loop")

  @multimethod
  def visit(self, node: ContinueStmt):
    if self.loopNesting == 0:
      self.errors.append("Error: 'continue' used outside of a loop")

  @multimethod
  def visit(self, node: WhileStmt):
    condType = self.visit(node.cond)
    if condType != 'bool':
      self.errors.append(f"Error: The 'while' condition must be of type 'bool', found '{condType}'")
    
    self.loopNesting += 1
    
    self.enter_scope(name='While Loop', scope_type='Loop')
    
    for stmt in node.body:
      self.visit(stmt)
    
    self.leave_scope()
    
    self.loopNesting -= 1


  @multimethod
  def visit(self, node: ForStmt):
    self.loopNesting += 1

    # Entrar en un nuevo scope para el bucle for
    self.enter_scope(name='For-Loop', scope_type='Bloque')

    if node.initialization:
        self.visit(node.initialization)

    if node.condition:
        condType = self.visit(node.condition)
        if condType != 'bool':
            self.errors.append(f"Error: The 'for' condition must be of type 'bool', found '{condType}'")

    if node.increment:
        self.visit(node.increment)

    # Visitar el cuerpo del bucle
    for stmt in node.body:
        self.visit(stmt)

    # Salir del scope del bucle for
    self.leave_scope()
    self.loopNesting -= 1

  @multimethod
  def visit(self, node: PrintStmt):
    formatSpecifiers = re.findall(r'%[-+#0]*\d*(?:\.\d+)?[diuoxXfFeEgGaAcs]', node.format_string)
    num_specifers = len(formatSpecifiers)
    num_args = len(node.args_list)
    
    if num_specifers != num_args:
      self.errors.append(f"Error: Expected {num_specifers} arguments, found {num_args}")
      return
    
    specifier_to_type = {
      'd': 'int', 'i': 'int', 'u': 'int', 'o': 'int', 'x': 'int',
      'X': 'int', 'f': 'float', 'F': 'float', 'e': 'float', 'E': 'float',
      'g': 'float', 'G': 'float', 'a': 'float', 'A': 'float', 'c': 'int',
      's': 'string'
    }
    
    for i, (specifier,arg) in enumerate(zip(formatSpecifiers, node.args_list)):
      specifier_key = specifier[-1]
      expected_type = specifier_to_type.get(specifier_key, None)
      
      if expected_type is None:
        self.errors.append(f"Error: Invalid format specifier '{specifier}'")
        continue
      
      arg_type = self.visit(arg)
      
      if arg_type != expected_type:
        self.errors.append(f"Error: Argument {i+1} must be of type '{expected_type}', found '{arg_type}'") 
    return 'void'
    
  @multimethod
  def visit(self, node: SPrintStmt):
    buffer_name = node.buffer.ident
    if buffer_name not in self.symtable.maps[0]:
      self.errors.append(f"Error: Buffer '{buffer_name}' not declared")
      return
    bufferType = self.lookup(buffer_name)
    if bufferType != 'string':
      self.errors.append(f"Error: Buffer '{buffer_name}' must be of type 'string', found '{bufferType}'")
    formatSpecifiers = re.findall(r'%[-+#0]*\d*(?:\.\d+)?[diuoxXfFeEgGaAcs]', node.format_string)
    num_specifiers = len(formatSpecifiers)
    num_args = len(node.args_list)
    if num_specifiers != num_args:
      self.errors.append(f"Error: Expected {num_specifiers} arguments, found {num_args}")
      return
    specifier_to_type = {
      'd': 'int', 'i': 'int', 'u': 'int', 'o': 'int', 'x': 'int',
      'X': 'int', 'f': 'float', 'F': 'float', 'e': 'float', 'E': 'float',
      'g': 'float', 'G': 'float', 'a': 'float', 'A': 'float', 'c': 'int',
      's': 'string'
    }
    for i, (specifier, arg) in enumerate(zip(formatSpecifiers, node.args_list)):
      specifier_key = specifier[-1]
      expected_type = specifier_to_type.get(specifier_key, None)
      if expected_type is None:
        self.errors.append(f"Error: Invalid format specifier '{specifier}'")
        continue
      arg_type = self.visit(arg)
      if arg_type != expected_type:
        self.errors.append(f"Error: Argument {i+1} must be of type '{expected_type}', found '{arg_type}'")
    return 'void'
    
  @multimethod
  def visit(self, node: SizeStmt):
    varType = self.lookup(node.ident)
    if varType is None:
      self.errors.append(f"Error: Variable '{node.ident}' is not declared")
    elif not isinstance(varType, ArrayDecl):
      self.errors.append(f"Error: '{node.ident}' is not an array")
    return 'int'

  @multimethod
  def visit(self, node: ThisStmt):
    if self.currentClass is None:
      self.errors.append("Error: 'this' used outside of a class")
    else:
      return self.currentClass.ident

  @multimethod
  def visit(self, node: SuperStmt):
    if self.currentClass is None:
      self.errors.append("Error: 'super' used outside of a class")
      return
    
    if self.currentClass.super_class is None:
      self.errors.append(f"Error: Class '{self.currentClass.ident}' has no superclass")
      return
    
    superClass = self.lookupClass(self.currentClass.super_class)
    if superClass is None:
      self.errors.append(f"Error: Superclass '{self.currentClass.super_class}' is not declared")
      return
    
    constructor = self.findConstructor(superClass, superClass.ident)
    if constructor:
      if len(node.args_list) != len(constructor.params):
        self.errors.append(f"Error: The constructor of '{superClass.ident}' expects {len(constructor.params)} arguments, found {len(node.args_list)}")
      else:
        for argExpr, param in zip(node.args_list, constructor.params):
          argType = self.visit(argExpr)
          paramType = param.var_type
          if not self.checkAssignmentCompatibility(paramType, argType):
            self.errors.append(f"Error: Argument of type '{argType}' cannot be assigned to parameter '{param.ident}' of type '{paramType}'")
    else:
      self.errors.append(f"Error: No constructor found for class '{superClass.ident}'")

  @multimethod
  def visit(self, node: CallExpr):
    if node.object_name:
      objectType = self.lookup(node.object_name)
      if objectType is None:
        self.errors.append(f"Error: Object '{node.object_name}' is not declared")
        return None
      classDecl = self.lookupClass(objectType)
      if classDecl is None:
        self.errors.append(f"Error: Object type '{objectType}' is not a valid class")
        return None
      methodDecl = self.find_method(classDecl, node.ident)
      if methodDecl is None:
        self.errors.append(f"Error: Method '{node.ident}' not found in class '{objectType}'")
        return None
      if len(node.args) != len(methodDecl.params):
        self.errors.append(f"Error: Method '{node.ident}' in class '{objectType}' expects {len(methodDecl.params)} arguments, found {len(node.args)}")
      else:
        for argExpr, param in zip(node.args, methodDecl.params):
          argType = self.visit(argExpr)
          paramType = param.var_type
          if not self.checkAssignmentCompatibility(paramType, argType):
            self.errors.append(f"Error: Argument of type '{argType}' cannot be assigned to parameter '{param.ident}' of type '{paramType}' in method '{node.ident}'")
      return methodDecl.return_type
    else:
      funcDecl = self.lookup(node.ident)
      if funcDecl is None or not isinstance(funcDecl, FuncDecl):
        self.errors.append(f"Error: Function '{node.ident}' is not declared")
        return None
      if len(node.args) != len(funcDecl.params):
        self.errors.append(f"Error: Function '{node.ident}' expects {len(funcDecl.params)} arguments, found {len(node.args)}")
      else:
        for argExpr, param in zip(node.args, funcDecl.params):
          argType = self.visit(argExpr)
          paramType = param.var_type
          if not self.checkAssignmentCompatibility(paramType, argType):
            self.errors.append(f"Error: Argument of type '{argType}' cannot be assigned to parameter '{param.ident}' of type '{paramType}' in function '{node.ident}'")
      return funcDecl.return_type

  @multimethod
  def visit(self, node: ConstExpr):
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
      self.errors.append(f"Error: Unknown constant type '{node.value}'")
      return None

  @multimethod
  def visit(self, node: VarExpr):
    varType = self.lookup(node.ident)
    if varType is None:
      self.errors.append(f"Error: Variable '{node.ident}' not declared")
      return None
    return varType

  @multimethod
  def visit(self, node: ArrayLookupExpr):
    arrayDecl = self.lookup(node.ident)
    if arrayDecl is None:
      self.errors.append(f"Error: Array '{node.ident}' not declared")
      return None
    if not isinstance(arrayDecl, ArrayDecl):
      self.errors.append(f"Error: '{node.ident}' is not an array")
      return None
    indexType = self.visit(node.index)
    if indexType != 'int':
      self.errors.append(f"Error: Array index must be of type 'int', found '{indexType}'")
    return arrayDecl.var_type

  @multimethod
  def visit(self, node: VarAssignExpr):
    varType = self.lookup(node.ident)
    if varType is None:
      self.errors.append(f"Error: Variable '{node.ident}' not declared")
      return None
    exprType = self.visit(node.expr)
    if not self.checkAssignmentCompatibility(varType, exprType):
      self.errors.append(f"Error: Cannot assign value of type '{exprType}' to variable '{node.ident}' of type '{varType}'")
    return varType

  @multimethod
  def visit(self, node: ArrayAssignExpr):
    arrayDecl = self.lookup(node.ident)
    if arrayDecl is None:
      self.errors.append(f"Error: Array '{node.ident}' not declared")
      return None
    if not isinstance(arrayDecl, ArrayDecl):
      self.errors.append(f"Error: '{node.ident}' is not an array")
      return None
    indexType = self.visit(node.index)
    if indexType != 'int':
      self.errors.append(f"Error: Array index must be of type 'int', found '{indexType}'")
    exprType = self.visit(node.expr)
    elemType = arrayDecl.var_type
    if not self.checkAssignmentCompatibility(elemType, exprType):
      self.errors.append(f"Error: Cannot assign value of type '{exprType}' to array element of type '{elemType}'")
    return elemType

  @multimethod
  def visit(self, node: ArraySizeExpr):
    arrayDecl = self.lookup(node.ident)
    if arrayDecl is None:
      self.errors.append(f"Error: Array '{node.ident}' not declared")
      return None
    if not isinstance(arrayDecl, ArrayDecl):
      self.errors.append(f"Error: '{node.ident}' is not an array")
      return None
    return 'int'

  @multimethod
  def visit(self, node: CompoundAssignExpr):
    varName = node.ident
    operator = node.operator
    expr = node.expr

    varType = self.lookup(varName)
    if varType is None:
      self.errors.append(f"Error: Variable '{varName}' not declared")
      return None

    exprType = self.visit(expr)
    binOperator = operator[0]
    binaryExpr = BinaryExpr(left=VarExpr(varName), operand=binOperator, right=expr)
    resultType = self.visit(binaryExpr)

    if resultType is None:
      self.errors.append(f"Error: Operation '{operator}' not supported between '{varType}' and '{exprType}'")
      return None

    if not self.checkAssignmentCompatibility(varType, resultType):
      self.errors.append(f"Error: Cannot assign value of type '{resultType}' to variable '{varName}' of type '{varType}'")
    return varType

  @multimethod
  def visit(self, node: BinaryExpr):
    leftType = self.visit(node.left)
    rightType = self.visit(node.right)
    resultType = self.checkBinaryOperation(node.operand, leftType, rightType)
    if resultType is None:
      self.errors.append(f"Error: Operation '{node.operand}' not supported between '{leftType}' and '{rightType}'")
    return resultType

  @multimethod
  def visit(self, node: PrefixIncExpr):
    if not isinstance(node.expr, VarExpr) and not isinstance(node.expr, ArrayLookupExpr):
      self.errors.append("Error: Operator '++' must be applied to a variable or array element")
      return None
    varType = self.visit(node.expr)
    if varType not in {'int', 'float'}:
      self.errors.append(f"Error: Operator '++' cannot be applied to variables of type '{varType}'")
    return varType

  @multimethod
  def visit(self, node: PrefixDecExpr):
    if not isinstance(node.expr, VarExpr) and not isinstance(node.expr, ArrayLookupExpr):
      self.errors.append("Error: Operator '--' must be applied to a variable or array element")
      return None
    varType = self.visit(node.expr)
    if varType not in {'int', 'float'}:
      self.errors.append(f"Error: Operator '--' cannot be applied to variables of type '{varType}'")
    return varType

  @multimethod
  def visit(self, node: PostfixIncExpr):
    if not isinstance(node.expr, VarExpr) and not isinstance(node.expr, ArrayLookupExpr):
      self.errors.append("Error: Operator '++' must be applied to a variable or array element")
      return None
    varType = self.visit(node.expr)
    if varType not in {'int', 'float'}:
      self.errors.append(f"Error: Operator '++' cannot be applied to variables of type '{varType}'")
    return varType

  @multimethod
  def visit(self, node: PostfixDecExpr):
    if not isinstance(node.expr, VarExpr) and not isinstance(node.expr, ArrayLookupExpr):
      self.errors.append("Error: Operator '--' must be applied to a variable or array element")
      return None
    varType = self.visit(node.expr)
    if varType not in {'int', 'float'}:
      self.errors.append(f"Error: Operator '--' cannot be applied to variables of type '{varType}'")
    return varType

  @multimethod
  def visit(self, node: ShortCircuitAndExpr):
    leftType = self.visit(node.left)
    if leftType != 'bool':
      self.errors.append(f"Error: Left expression of '&&' must be of type 'bool', found '{leftType}'")
    rightType = self.visit(node.right)
    if rightType != 'bool':
      self.errors.append(f"Error: Right expression of '&&' must be of type 'bool', found '{rightType}'")
    return 'bool'

  @multimethod
  def visit(self, node: ShortCircuitOrExpr):
    leftType = self.visit(node.left)
    if leftType != 'bool':
      self.errors.append(f"Error: Left expression of '||' must be of type 'bool', found '{leftType}'")
    rightType = self.visit(node.right)
    if rightType != 'bool':
      self.errors.append(f"Error: Right expression of '||' must be of type 'bool', found '{rightType}'")
    return 'bool'

  @multimethod
  def visit(self, node: UnaryExpr):
    exprType = self.visit(node.expr)
    resultType = self.checkUnaryOperation(node.operand, exprType)
    if resultType is None:
      self.errors.append(f"Error: Unary operation '{node.operand}' not supported for type '{exprType}'")
    return resultType

  @multimethod
  def visit(self, node: CastExpr):
    exprType = self.visit(node.expr)
    targetType = node.target_type
    if not self.isCastValid(exprType, targetType):
      self.errors.append(f"Error: Cannot cast from {exprType} to {targetType}")
    return targetType

  @multimethod
  def visit(self, node: GroupingExpr):
    return self.visit(node.expr)

  @multimethod
  def visit(self, node: IntToFloatExpr):
    exprType = self.visit(node.expr)
    if exprType != 'int':
      self.errors.append(f"Error: Conversion from 'int' to 'float' requires an operand of type 'int', found '{exprType}'")
    return 'float'

  @multimethod
  def visit(self, node: ClassDecl):
    className = node.ident
    superClassName = node.super_class
    
    if className in self.symtable.maps[0]:
        self.errors.append(f"Error: Class '{className}' already declared")
        return
    else:
        self.symtable[className] = node
        
    if superClassName:
        superClass = self.validateSuperClass(className, superClassName)
        if superClass is None:
            return
    
    self.currentClass = node    
    self.enter_scope(name=className, scope_type='Clase')
    
    for member in node.body:
        self.visit(member)
    
    self.leave_scope()
    self.currentClass = None

      
  
