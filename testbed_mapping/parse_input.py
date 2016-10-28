#!/usr/bin/python3

import capacity_function
import pms

def line_is_comment(line):
    """ Determine if a line is comment according to Chaco input spec. """
    return len(line) == 0 or line[0] in ('%', '#')


def to_num(str):
    """ Try parsing the given string to int or float. """
    try:
        return int(str)
    except:
        return float(str)


def parse_pms(filepath, high_order_first=True):
    pms = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line_is_comment(line):
                coefficients = [to_num(v) for v in line.split()]
                capacity_func = capacity_function.CapacityFunction(coefficients, high_order_first)
                pms.append(pms.PhysicalMachine(capacity_func))
    return pms


def read_flat_ints(filepath):
    with open(filepath, 'r') as f:
        return [to_num(v) for v in f.readlines()]
