#!/usr/bin/python3

import argparse

import oracles


def main():
    parser = argparse.ArgumentParser(description='Wrapper to graph partitioning oracle.')
    parser.add_argument('--oracle', type=str, default='chaco', help='Graph partitioning oracle.')
    parser.add_argument('--graph-file', type=str, required=True, help='File to read input graph from.')
    parser.add_argument('--vhosts-cpu-file', type=str, required=False,
                        help='File to read CPU share of vhosts from. Line i is CPU share needed by vhost i.')
    parser.add_argument('--pm-file', type=str, required=False,
                        help='File to read PM information. One capacity function per line.')
    parser.add_argument('--work-dir', type=str, default=None,
                        help='Directory to save output files.')
    args = parser.parse_args()

    if args.oracle.lower() == 'chaco':
        oracle = oracles.ChacoOracle(args.graph_file, work_dir=args.work_dir)
    else:
        raise ValueError('Oracle "%s" is not supported.' % args.oracle)

    print(oracle.get_assignment([3033, 9127, 10920]))


if __name__ == '__main__':
    main()
