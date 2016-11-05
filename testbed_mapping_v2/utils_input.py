#!/usr/bin/python3


def line_is_comment(line):
    """ Determine if a line is comment according to Chaco input spec. """
    return len(line) == 0 or line[0] in ('%', '#')


def to_num(str):
    """ Try parsing the given string to int or float. """
    try:
        return int(str)
    except:
        return float(str)


def read_int_file(file_path):
    with open(file_path, 'r') as f:
        return [to_num(v) for v in f.readlines()]