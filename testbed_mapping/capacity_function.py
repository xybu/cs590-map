#!/usr/bin/python3

class CapacityFunction:

  """
  Here capacity function is modeled as f(x) = a_n*x^n + a_(n-1)*x^(n-1) + ...
  Could use sympy if things go complex.
  """

  def __init__(self, coefficients, high_order_first=True):
    """
    @param coefficients All coefficients for each order of x.
    """
    if len(coefficients) == 0:
      raise ValueError('Coefficient list must not be empty.')
    self.coefficients = coefficients
    if high_order_first:
      self.coefficients.reverse()

  def eval(self, x):
    """ An unoptimized way of computing the function. """
    result = 0
    multiplier = 1
    for a in self.coefficients:
      result = result + a * multiplier
      multiplier = multiplier * x
    return result
