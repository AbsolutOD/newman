# -*- coding: utf-8 -*-
"""
  Decorators
"""

def task(options):
  def define_task(func):
    def new_func(*args, **kwargs):
      return func(*args, **kwargs)
    
    new_func.func_name = func.func_name
    new_func.func_doc = func.func_doc
    new_func.__dict__ = func.__dict__
    new_func.task = True
    new_func.options = options
    return new_func
  
  return define_task
