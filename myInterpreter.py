from myAST import *
from mchecker import *
from builtins import *
from types import *
from dataclasses import dataclass

def isTruth(value):
  if isinstance(value, bool):
    return value
  elif value is None:
    return False
  else:
    return True


class ReturnException(Exception):
  def _init_(self, value):
    self.value = value
    
  
class BreakException(Exception):
  pass

class ContinueException(Exception):
  pass

class MiniCExit(BaseException):
  pass  

class AttributeError(BaseException):
  pass

class Function: 
  def _init_(self, node, env):
    self.node = node
    self.env = env
    
    @property
    def arity(self) -> int:
      return len(self.node.params)
    
    def _call_(self, interpreter, *args):
      newEnv = self.env.new_child()
      for name, arg in zip(self.node.params, args):
        newEnv[name] = arg
      oldEnv= interpreter.env
      interpreter.env = newEnv
      try :
        self.node.body.accept(interpreter)
        result = None
      except ReturnException as e:
        result = e.value
      finally:
        interpreter.env = oldEnv
      return result 
    
    def bind(self, instance):
      env = self.env.new_child()
      env['this'] = instance
      return Function(self.node, env)