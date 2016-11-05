#!/usr/bin/python3


class 


class Machine:

    def __init__(self, max_cpu_share, min_switch_cpu_share, max_switch_cpu_share, coefficients):
        pass

    @staticmethod
    def read_machines_from_file(cls, filepath):
        all_pms = []
        with open(filepath, 'r') as f:
            pm = Machine()
