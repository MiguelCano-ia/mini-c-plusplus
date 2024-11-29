from myAST import *
from mchecker import *
from builtins import *
from types import *

#Veracidad miniC++
def isTruth(value):
  if isinstance(value, bool):
    return value
  elif 