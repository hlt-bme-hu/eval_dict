#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Judit Acs <judit@sch.bme.hu>
#
# Distributed under terms of the MIT license.

from argparse import ArgumentParser
import numpy as np


def parse_args():
    p = ArgumentParser()
    p.add_argument('--from', dest='from_', choices=['numpy'], default='numpy')
    p.add_argument('--to', choices=['glove'], default='glove')
    p.add_argument('-i', '--input-matrix', type=str)
    p.add_argument('-d', '--dictionary', type=str)
    p.add_argument('-o', '--output', type=str)
    return p.parse_args()


def numpy2glove(mtx_fn, dict_fn, out_fn):
    m = np.load(mtx_fn)
    with open(dict_fn) as f:
        d = [l.decode('utf8').strip() for l in f]
    with open(out_fn, 'w') as f:
        for i, word in enumerate(d):
            f.write('{0} {1}\n'.format(
                word.encode('utf8'), ' '.join(map(str, m[i]))))


def main():
    args = parse_args()
    if args.from_ == 'numpy' and args.to == 'glove':
        numpy2glove(args.input_matrix, args.dictionary, args.output)

if __name__ == '__main__':
    main()
