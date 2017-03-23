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

  def reverse_eval(self, y, x=None):
      """ Given the capacity value y, find the smallest x such that f(x)>=y. """
      if x is None:
          x = self.domain[1]
      while self.eval(x) > y:
          x -= 1
      while self.eval(x) < y:
          x += 1
      return max(x, self.domain[0])

  def __eq__(self, other):
      return self.domain == other.domain and self.coefficients == other.coefficients

  def __ne__(self, other):
      return not self.__eq__(other)

  def __repr__(self):
    highest_order = len(self.coefficients) - 1
    return 'f(u) = ' + ' + '.join('%.4lf u^%d' % (c, highest_order - d) for d, c in enumerate(self.coefficients[::-1]))


class Machine:

    def __init__(self, pm_id, share_multiplier, max_cpu_share, min_switch_cpu_share, max_switch_cpu_share, coefficients):
        """
        Instantiate a physical machine object.
        :param int pm_id:
        :param float share_multiplier:
        :param int max_cpu_share:
        :param int min_switch_cpu_share:
        :param int max_switch_cpu_share:
        :param list[int] coefficients:
        """
        self.pm_id = pm_id
        self.share_multiplier = share_multiplier
        self.max_cpu_share = max_cpu_share
        self.min_switch_cpu_share = min_switch_cpu_share
        self.max_switch_cpu_share = max_switch_cpu_share
        self.capacity_func = CapacityFunction((min_switch_cpu_share, max_switch_cpu_share), coefficients, False)

    @property
    def full_str(self):
        return '<PM #%02d | (%02d, %d)/%d/%.2f | %s>' % (
            self.pm_id, self.min_switch_cpu_share, self.max_switch_cpu_share, self.max_cpu_share, self.share_multiplier,
            str(self.capacity_func))

    def __repr__(self):
        return '<PM #%02d | (%02d, %d)/%d/%.2f>' % (
            self.pm_id, self.min_switch_cpu_share, self.max_switch_cpu_share, self.max_cpu_share, self.share_multiplier)

    def __eq__(self, other):
        return self.pm_id == other.pm_id

    @staticmethod
    def read_machines_from_file(file_path, normalize=True):
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
                share_multiplier, max_cpu_share, min_switch_cpu_share, max_switch_cpu_share, coefficients = line.split(maxsplit=4)
                share_multiplier = utils_input.to_num(share_multiplier)
                max_cpu_share = utils_input.to_num(max_cpu_share)
                min_switch_cpu_share = utils_input.to_num(min_switch_cpu_share)
                max_switch_cpu_share = utils_input.to_num(max_switch_cpu_share)
                coefficients = [utils_input.to_num(c) for c in coefficients.split()]
                if normalize and share_multiplier != 1:
                    max_cpu_share = max_cpu_share * share_multiplier
                    min_switch_cpu_share = min_switch_cpu_share * share_multiplier
                    max_switch_cpu_share = max_switch_cpu_share * share_multiplier
                    # f(x) = g(my) -> y=x/m -> g(y) = f(x/m)
                    coefficients = [c / (share_multiplier ** i) for i, c in enumerate(coefficients)]
                pm = Machine(pm_id=len(all_pms), share_multiplier=share_multiplier, max_cpu_share=max_cpu_share,
                             min_switch_cpu_share=min_switch_cpu_share, max_switch_cpu_share=max_switch_cpu_share,
                             coefficients=coefficients)
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
