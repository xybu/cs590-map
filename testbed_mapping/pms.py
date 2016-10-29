#!/usr/bin/python3

class PhysicalMachine:

  def __init__(self, pm_id, capacity_func):
      """
      :param int pm_id:
      :param capacity_function.CapacityFunction capacity_func:
      """
      self.pm_id = pm_id
      self.capacity_func = capacity_func
      self.is_enabled = sum(capacity_func.coefficients) != 0

  def __str__(self):
    return 'PM #%d [%s]' % (self.pm_id, str(self.capacity_func))
