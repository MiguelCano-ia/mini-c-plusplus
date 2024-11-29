from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Union

@dataclass
class CType:
  def __repr__(self):
    return self.__str__()
  
@dataclass
class NumberType(CType):
  value : Union[int, float]
  
  def __str__(self):
    return f'{self.value}'
  
    
@dataclass
class BoolType(CType):
  value : bool
  
  def __str__(self):
    return f'{self.value}'
  
@dataclass
class StringType(CType):
  value : str
  
  def __str__(self):
    return f'{self.value}'
  
@dataclass
class NullType(CType):
  value : None = None
  
  def __str__(self):
    return 'null'
  
@dataclass
class ArrayType(CType):
  elementType : CType
  size : int
  elements : List[CType] = field(default_factory = list)
  
  def __post_init__(self):
    if self.size < 0:
      raise ValueError('Size must be greater than or equal to 0 but got {self.size}')
    self.elements = [self._default_value_() for _ in range(self.size)]
    
  def _default_value_(self):
    if isinstance(self.elementType, NumberType):
      return NumberType(0)
    elif isinstance(self.elementType, BoolType):
      return BoolType(False)
    elif isinstance(self.elementType, StringType):
      return StringType('')
    elif isinstance(self.elementType, NullType):
      return NullType()
    else:
      raise TypeError(f'Unknown type {self.elementType}')
    
  def __get_item__(self, index):
    if not 0 <= index < self.size:
      raise IndexError(f'Index out of range: {index}')
    return self.elements[index]
  
  def __set_item__(self, index, value):
    if not 0 <= index < self.size:
      raise IndexError(f'Index out of range: {index}')
    if not isinstance(value, self.elementType):
      raise TypeError(f'Expected {self.elementType} but got {type(value)}')
    
  def __str__(self):
    return f'[{", ".join(map(str, self.elements))}]'
  
    
  
  