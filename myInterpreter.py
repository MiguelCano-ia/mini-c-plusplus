from myAST import *
from mchecker import *
from buildins import builtins, consts
from types import *
from dataclasses import dataclass
from multimethod import multimethod

#Verifies if a value is truthy
def isTruth(value):
  if isinstance(value, bool):
    return value
  elif value is None:
    return False
  else:
    return True


class ReturnException(Exception):
  def __init__(self, value):
    self.value = value
    
  
class BreakException(Exception):
  pass

class ContinueException(Exception):
  pass

class MiniCExit(BaseException):
  pass  

class AttributeError(BaseException):
  pass


#Class to rpresent the environment on a function call
class Function: 
  def __init__(self, node, env):
    self.node = node
    self.env = env
    
  @property
  def arity(self) -> int:
    return len(self.node.params)
  
  #Call the function
  def __call__(self, interpreter, *args):
    #Create a new environment using new_child method
    #This method is from the ChainMap class
    #It creates a new dictionary with the current dictionary as a parent
    newEnv = self.env.new_child()
    #Iterate over the parameters and the arguments
    #Using zip to iterate over two lists at the same time
    for name, arg in zip(self.node.params, args):
      #Add the parameter to the new environment
      newEnv[name] = arg
    #Save the current environment
    oldEnv= interpreter.env
    #Set the new environment
    interpreter.env = newEnv
    #Execute the function body
    try :
      result = None
      for stmt in self.node.body:
        stmt.accept(interpreter)
    except ReturnException as e:
      result = e.value
    finally:
      #Restore the old environment
      #This is done in a finally block to ensure that the environment is restored
      interpreter.env = oldEnv
    return result 
  
  #Bind the function to an instance
  #This is used to create a method for a class
  def bind(self, instance):
    #Create a new environment using new_child method
    env = self.env.new_child()
    #Add the instance to the environment
    env['this'] = instance
    return Function(self.node, env)

#Class to represent the environment of a class
class Class:
  #Constructor
  def __init__(self, name, sclass, methods):
    self.name = name
    self.sclass = sclass
    self.methods = methods
  
  #Get the class name
  def __str__(self):
    return self.name
  
  #Method for calling a constructor of a class
  def __call__(self, *args):
    this = Instance(self)
    init = self.find_method('init')
    if init:
      init.bind(this)(*args)
    return this
  
  #Find a method in the class by its name
  def find_method(self, name):
    #Get the method by its name
    meth = self.methods.get(name)
    #If the method is not found, search in the superclass
    if meth is None and self.sclass:
      return self.sclass.find_method(name)
    elif meth is None:
      raise AttributeError(name)
    else:
      return meth
    
#Class to represent an instance of a class    
class Instance:
  #Constructor
  def __init__(self, klass):
    self.klass = klass
    #Create a dictionary to store the instance data
    self.data = {}
    
  #Get the instance name 
  def __str__(self):
    return f'{self.klass.name} instance'
  
  #Get the value of an instance property
  def get(self, name):
    #If the property is in the instance data, return it
    if name in self.data:
      return self.data[name]
    #If the property is a method, return the method
    meth = self.klass.find_method(name)
    if not meth:
      raise AttributeError(f'Property {name} not found')
    #if the method is found, bind it to the instance
    return meth.bind(self)
  
  #Set the value of an instance property  
  def set(self, name, value):
    self.data[name] = value
    return value
  
  
#Class to represent the interpreter
class Interpreter(Visitor):
  
  def __init__(self, ctxt, semantic_analyzer):
    #Save the context
    self.ctxt = ctxt
    self.semantic_analyzer = semantic_analyzer
    #Create a dictionary to store the global environment with ChainMap
    self.env = ChainMap()
    self.checkEnv = ChainMap()
    self.localMap = {}
    
  #Method to check numeric operands, used in binary operations  
  def check_numeric_operands(self, node, left, right):
    if isinstance(left, (int,float)) and isinstance(right, (int,float)):
      return True
    else:
      self.error(node, f'{node.operand} operator can only be used with numeric operands')

  def check_numeric_operand(self, node, value):
    if isinstance(value, (int,float)):
      return True
    else:
      self.error(node, f'{node.operand} operator can only be used with numeric operands')
      
  def error(self, position, message):
    self.ctxt.error(position, message)
    raise MiniCExit()
  
  #Punto de entrada de alto nivel
  def interpret(self, node):
    self.semantic_analyzer.visit(node)
    
    if self.semantic_analyzer.errors:
      for err in self.semantic_analyzer.errors:
        print(f'Error: {err}')
      return
    
    for name, cval in consts.items():
      self.checkEnv[name] = cval
      self.env[name] = cval
      
    for name, func in builtins.items():
      self.checkEnv[name] = func
      self.env[name] = func
      
    try:
      node.accept(self)
      main_func = self.env.get('main')
      if not isinstance(main_func, Function):
        raise Exception("No valid 'main' function found")

      # Ejecuta main sin argumentos (ajusta si acepta parámetros)
      result = main_func(self)
      if result is not None:
        print(f"Program exited with value: {result}")
    except ReturnException as re:
      print(f"Program exited with value: {re.value}")
    except Exception as e:
      print(f"Error during execution: {e}")

  #declarations
  @multimethod
  def visit(self, node: ClassDecl):
    if node.super_class:
      sclass = node.super_class.accept(self)
      env = self.env.new_child()
      env['super'] = sclass
    else:
      sclass = None
      env = self.env
    methods = {}
    for meth in node.body:
      if isinstance(meth, FuncDecl):
        methods[meth.name] = Function(meth, env)
    klass = Class(node.name, sclass, methods)
    self.env[node.name] = klass
    
  @multimethod  
  def visit(self, node: FuncDecl):

    func = Function(node, self.env)
    self.env[node.ident] = func
  
  @multimethod
  def visit(self, node: VarDecl):
    if node.expr:
      expr = node.expr.accept(self)
    else:
      expr = None
    self.env[node.ident] = expr

  @multimethod
  def visit(self, node: ArrayDecl):
    sizeValue = node.size.accept(self)
    array = [0 if node.var_type == 'int' else 0.0] * sizeValue
    self.env[node.ident] = array
      
  @multimethod
  def visit(self, node: ObjectDecl):
    klass = self.env.get(node.class_type)
    evalArgs = [arg.accept(self) for arg in node.args]
    instance = klass(*evalArgs)
    self.env[node.instance_name] = instance
    
  #Statements
  @multimethod
  def visit(self, node: Program):
    if node.stmts:
      for stmt in node.stmts:
        stmt.accept(self)
    else:
      return
  
  @multimethod
  def visit(self, node: ExprStmt):
    return node.expr.accept(self)
  
  
  @multimethod
  def visit(self, node: IfStmt):
    condition = node.cond.accept(self)
    if isTruth(condition):
      for stmt in node.then_stmt:
        stmt.accept(self)
    elif node.else_stmt:
      for stmt in node.else_stmt:
        stmt.accept(self)
    
  @multimethod
  def visit(self, node: ReturnStmt):
    value = 0 if not node.expr else node.expr.accept(self)
    raise ReturnException(value)
  
  @multimethod
  def visit(self, node: BreakStmt):
    raise BreakException()
  
  @multimethod
  def visit(self, node : WhileStmt):
    while isTruth(node.cond.accept(self)):
      try:
        for stmt in node.body:
          stmt.accept(self)
      except ContinueException:
        continue
      except BreakException:
        break
      
  
  @multimethod
  def visit (self, node : ForStmt):
    node.initialization.accept(self)
    while isTruth(node.condition.accept(self)):
      try:
        for stmt in node.body:
          stmt.accept(self)
        node.increment.accept(self)
      except ContinueException:
        continue
      except BreakException:
        break
  
  @multimethod
  def visit(self, node: PrintStmt):
    if node.args_list:
      # Evaluar cada argumento en args_list
      values = tuple(arg.accept(self) for arg in node.args_list)
      try:
        # Procesar los caracteres de escape en format_string
        processed_format_string = bytes(node.format_string, "utf-8").decode("unicode_escape")
          
            # Aplicar el formato usando el operador % de Python
        formatted = processed_format_string % values
      except TypeError as e:
        # Manejar errores de formateo, aunque el checker ya debería haber validado esto
        self.error(node, f"Error de formateo: {e}")
      except UnicodeDecodeError as e:
        # Manejar errores de decodificación de caracteres de escape
        self.error(node, f"Error en caracteres de escape: {e}")
    else:
      # Si no hay argumentos, procesar los caracteres de escape directamente
      try:
        processed_format_string = bytes(node.format_string, "utf-8").decode("unicode_escape")
        formatted = processed_format_string
      except UnicodeDecodeError as e:
        self.error(node, f"Error en caracteres de escape: {e}")
    
    # Imprimir la cadena formateada sin añadir una nueva línea adicional
    print(f"{formatted}", end="")
    
  @multimethod
  def visit(self, node: SPrintStmt):
    args = [arg.accept(self) for arg in node.args_list]
    
    try:
      self.checkEnv[node.buffer.ident] = node.format_string.format(*args)
    except (IndexError, ValueError) as e:
      self.error(node, f'Error in sprint statement: {e}')
      
  @multimethod
  def visit(self, node: ContinueStmt):
    raise ContinueException()
  
  @multimethod
  def visit(self, node: SizeStmt):
    array = self.env.get(node.ident)
    
    return len(array)
  
  @multimethod
  def visit(self, node: ThisStmt):
    if 'this' not in self.env:
      raise Exception("No instance found")
    return self.env['this']
  
  @multimethod
  def visit(self, node: PrivateStmt):
    pass
  
  @multimethod
  def visit(self, node: SuperStmt):
    pass
  
  @multimethod
  def visit(self, node: PublicStmt):
    pass
  
  
  #Expressions
  
  @multimethod
  def visit(self, node: NullExpr):
    return None
  
  @multimethod
  def visit(self, node: CallExpr):
    pass
  
  @multimethod
  def visit(self, node: ConstExpr):
    return node.value
  
  @multimethod
  def visit(self, node: CompoundAssignExpr):
    ident = node.ident
    operator = node.operator
    expr = node.expr.accept(self)
    
    if operator == '=':
      self.env[node.ident] = expr
    elif operator == '+=':
      self.env[node.ident] += expr
    elif operator == '-=':
      self.env[node.ident] -= expr
    elif operator == '*=':
      self.env[node.ident] *= expr
    elif operator == '/=':
      self.env[node.ident] /= expr
  
  @multimethod
  def visit(self, node: VarExpr):
    if node.ident not in self.env:
        raise Exception(f"Variable '{node.ident}' is not defined in the current environment: {dict(self.env)}")
    value = self.env[node.ident]
    return value
  
  @multimethod
  def visit(self, node: ArrayLookupExpr):
    if node.ident not in self.env:
      raise Exception(f"Variable '{node.ident}' is not defined in the current environment: {dict(self.env)}")
    
    array = self.env[node.ident]
    index = node.index.accept(self)  
    
    if not isinstance(index, int):
      raise Exception(f"Array index must be an integer got {type(index).__name__}")
    if not isinstance(array, list):
      raise Exception(f"Variable '{node.ident}' is not an array")
    if index < 0 or index >= len(array):
      raise Exception(f"Array index out of bounds")
    return array[index]

  @multimethod
  def visit(self, node: VarAssignExpr):
    if node.ident not in self.env:
      raise Exception(f"Variable '{node.ident}' is not defined in the current environment: {dict(self.env)}")
    
    value = node.expr.accept(self)
    self.env[node.ident] = value
    
    return value
  
  @multimethod
  def visit(self, node: ArrayAssignExpr):
    if not node.ident in self.env:
      raise Exception(f"Variable '{node.ident}' is not defined in the current environment: {dict(self.env)}")
    
    array = self.env[node.ident]
    index = node.index.accept(self)
    value = node.expr.accept(self)
    
    if not isinstance(index, int):
      raise Exception(f"Array index must be an integer got {type(index).__name__}")
    if not isinstance(array, list):
      raise Exception(f"Variable '{node.ident}' is not an array")
    if index < 0 or index >= len(array):
      raise Exception(f"Array index out of bounds")
    array[index] = value
  
  @multimethod
  def visit(self, node: ArraySizeExpr):
    if node.ident not in self.env:
      raise Exception(f"Variable '{node.ident}' is not defined in the current environment: {dict(self.env)}")
    
    array = self.env[node.ident]
    
    if not isinstance(array, list):
      raise Exception(f"Variable '{node.ident}' is not an array")
    return len(array)
  
  @multimethod
  def visit(self, node: IntToFloatExpr):
    expr = node.expr.accept(self)
    return float(expr)
  
  @multimethod
  def visit(self, node: BinaryExpr):
    left = node.left.accept(self)
    right = node.right.accept(self)
    operand = node.operand
    
    if operand  == '+':
      (isinstance(left,str) and isinstance(right,str)) or  self.check_numeric_operands(node, left, right)
      return left + right
    elif operand == '-':
      self.check_numeric_operands(node, left, right)
      return left - right
    elif operand == '*':
      self.check_numeric_operands(node, left, right)
      return left * right
    elif operand == '/':
      self.check_numeric_operands(node, left, right)
      if isinstance(left, int) and isinstance(right, int):
        return left // right
      return left / right
    elif operand == '%':
      self.check_numeric_operands(node, left, right)
      return left % right
    elif operand == '==':
      return left == right
    elif operand == '!=':
      return left != right
    elif operand == '>':
      self.check_numeric_operands(node, left, right)
      return left > right
    elif operand == '<':
      self.check_numeric_operands(node, left, right)
      return left < right
    elif operand == '>=':
      self.check_numeric_operands(node, left, right)
      return left >= right
    elif operand == '<=':
      self.check_numeric_operands(node, left, right)
      return left <= right
    else:
      raise NotImplementedError(f'Operator {operand} not recognized')

  @multimethod
  def visit(self, node: UnaryExpr):
    operand = node.operand
    expr = node.expr.accept(self)
    
    if operand == '+':
      self.check_numeric_operand(node, expr)
      return +expr
    elif operand == '-':
      self.check_numeric_operand(node, expr)
      return -expr
    elif operand == '!':
      return not isTruth(expr)
    else:
      raise NotImplementedError(f'Operator {operand} not recognized')
    
  @multimethod
  def visit(self, node: CastExpr):
    targetType = node.target_type
    expr = node.expr.accept(self)
    
    try:
      if targetType == 'int':
        return int(expr)
      elif targetType == 'float':
        return float(expr)
      elif targetType == 'bool':
        return bool(expr)
      elif targetType == 'string':
        return str(expr)
      else:
        raise NotImplementedError(f'Target type {targetType} not recognized')
    except ValueError:
      self.error(node, f'Cannot cast {expr} to {targetType}')
      
  @multimethod
  def visit(self, node: GroupingExpr):
    return node.expr.accept(self)
  
  @multimethod
  def visit(self, node : PrefixIncExpr):
    expr = node.expr.accept(self)
    return expr + 1
  
  @multimethod
  def visit(self, node : PrefixDecExpr):
    expr = node.expr.accept(self)
    return expr - 1
  
  @multimethod
  def visit(self, node : PostfixIncExpr):
    expr = node.expr.accept(self)
    return expr + 1
  
  @multimethod
  def visit(self, node : PostfixDecExpr):
    expr = node.expr.accept(self)
    return expr - 1
  
  @multimethod
  def visit(self, node : ShortCircuitAndExpr):
    left = node.left.accept(self)
    right = node.right.accept(self)
    
    return left and right
  
  @multimethod
  def visit(self, node: ShortCircuitOrExpr):
    left = node.left.accept(self)
    right = node.right.accept(self)
    
    return left or right
  