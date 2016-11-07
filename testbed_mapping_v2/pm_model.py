#!/usr/bin/python3

import utils_input


class CapacityFunction:

  """
  Here capacity function is modeled as f(x) = a_n*x^n + a_(n-1)*x^(n-1) + ...
  Could use sympy if things go complex.
  """

  def __init__(self, domain, coefficients, high_order_first=True):
    """
    :param (int, int) domain: Domain of the function.
    :param list[int|float] coefficients: All coefficients for each order of x.
    :param True | False high_order_first: If True, the first coefficient is for the highest order; otherwise lowest.
    """
    if len(coefficients) == 0:
        raise ValueError('Coefficient list must not be empty.')
    if sum(coefficients) == 0:
        raise ValueError('Sum of coefficients must not be 0.')
    if len(domain) != 2 or domain[0] > domain[1]:
        raise ValueError('Invalid function domain: "%s"' % str(domain))
    # TODO: Validate that the function is non-negative on the domain.
    self.domain = domain
    self.coefficients = coefficients
    if high_order_first:
        self.coefficients.reverse()

  def eval(self, x):
    """ An unoptimized way of computing the function. """
    result = 0
    multiplier = 1
    for a in self.coefficients:
      result += a * multiplier
      multiplier = multiplier * x
    return result

  def __eq__(self, other):
      return self.domain == other.domain and self.coefficients == other.coefficients

  def __ne__(self, other):
      return not self.__eq__(other)

  def __repr__(self):
    highest_order = len(self.coefficients) - 1
    return 'f(u) = ' + ' + '.join('%.4lf u^%d' % (c, highest_order - d) for d, c in enumerate(self.coefficients[::-1]))


class Machine:

    def __init__(self, pm_id, max_cpu_share, min_switch_cpu_share, max_switch_cpu_share, coefficients):
        """
        Instantiate a physical machine object.
        :param int pm_id:
        :param int max_cpu_share:
        :param int min_switch_cpu_share:
        :param int max_switch_cpu_share:
        :param list[int] coefficients:
        """
        self.pm_id = pm_id
        self.max_cpu_share = max_cpu_share
        self.min_switch_cpu_share = min_switch_cpu_share
        self.max_switch_cpu_share = max_switch_cpu_share
        self.capacity_func = CapacityFunction((min_switch_cpu_share, max_switch_cpu_share), coefficients, False)

    def __eq__(self, other):
        """
        Return True if current PM equals the given PM (all parameters are equal except for PM ID).
        :param Machine other:
        :return True | False:
        """
        return self.max_cpu_share == other.max_cpu_share and self.min_switch_cpu_share == other.min_switch_cpu_share and self.max_switch_cpu_share == other.max_switch_cpu_share and self.capacity_func == other.capacity_func

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<PM #%s | (%d, %d)/%d | %s>' % (self.pm_id, self.min_switch_cpu_share, self.max_switch_cpu_share, self.max_cpu_share, str(self.capacity_func))

    @staticmethod
    def read_machines_from_file(file_path):
        """
        Parse the input file to a list of Machine objects. The input line format is:
        MAX_CPU_SHARE MIN_SWITCH_CPU_SHARE MAX_SWITCH_CPU_SHARE c_0 c_1 c_2 ...
        :param file_path: Path to the input file
        :return list[Machine]: Parsed machines.
        """
        all_pms = []
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if utils_input.line_is_comment(line):
                    continue
                max_cpu_share, min_switch_cpu_share, max_switch_cpu_share, coefficients = line.split(maxsplit=3)
                max_cpu_share = utils_input.to_num(max_cpu_share)
                min_switch_cpu_share = utils_input.to_num(min_switch_cpu_share)
                max_switch_cpu_share = utils_input.to_num(max_switch_cpu_share)
                coefficients = [utils_input.to_num(c) for c in coefficients.split()]
                pm = Machine(pm_id=len(all_pms), max_cpu_share=max_cpu_share, min_switch_cpu_share=min_switch_cpu_share,
                             max_switch_cpu_share=max_switch_cpu_share, coefficients=coefficients)
                proper_min_switch_cpu_share = min_switch_cpu_share
                for i in range(min_switch_cpu_share, max_switch_cpu_share + 1):
                    v = pm.capacity_func.eval(i)
                    if v < 0:
                        proper_min_switch_cpu_share = i + 1
                if proper_min_switch_cpu_share != min_switch_cpu_share:
                    pm.min_switch_cpu_share = proper_min_switch_cpu_share
                    print('NOTE: Capacity function of PM #%d is not defined below %d. Input fixed.' % (len(all_pms), proper_min_switch_cpu_share))
                all_pms.append(pm)
        return all_pms
