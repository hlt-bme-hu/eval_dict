#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Judit Acs <judit@sch.bme.hu>
#
# Distributed under terms of the MIT license.

from argparse import ArgumentParser
import numpy as np

from scipy.spatial.distance import cosine


def parse_args():
    p = ArgumentParser()
    p.add_argument('matrix1', type=str)
    p.add_argument('matrix2', type=str)
    p.add_argument('-t', '--type', choices=['cos', 'transform', 'orthogonal'],
                   default='transform')
    p.add_argument('-o', '--output', type=str, default='')
    p.add_argument('--left-dictionary', type=str, default='')
    p.add_argument('--right-dictionary', type=str, default='')
    p.add_argument('--left-type', choices=['numpy', 'glove', 'word2vec'],
                                           default='numpy')
    p.add_argument('--right-type', choices=['numpy', 'glove', 'word2vec'],
                                           default='numpy')
    return p.parse_args()


def load_matrix_and_dictionary(fn, typ, dict_fn=None):
    if typ == 'numpy':
        return np.load(fn), load_dictionary_as_dict(dict_fn)
    elif typ == 'glove':
        from glove import Glove
        m = Glove().load_stanford(fn)
        return m.word_vectors, m.dictionary
    elif typ == 'word2vec':
        from gensim.models import Word2Vec
        if 'txt' in fn or 'w2v' in fn:
            m = Word2Vec.load_word2vec_format(fn, binary=False)
        else:
            m = Word2Vec.load_word2vec_format(fn, binary=True)
        return extract_wordvec_matrix_and_dict(m)
    raise Exception('Unknown matrix format: {}'.format(typ))


def extract_wordvec_matrix_and_dict(model):
    mtx = []
    dictionary = {}
    for i, (word, vec) in enumerate(model.vocab.iteritems()):
        dictionary[word] = i
        mtx.append(model[word])
    return np.array(mtx), dictionary


def load_dictionary_as_dict(fn):
    i = 0
    d = {}
    with open(fn) as f:
        for l in f:
            d[l.decode('utf8').strip()] = i
            i += 1
    return d


def filter_to_common_words(A, B, dictA, dictB):
    filtA = []
    filtB = []
    common = []
    lhs_map = {v: k for k, v in dictA.iteritems()}
    for i, vec1 in enumerate(A):
        if lhs_map[i] not in dictB:
            continue
        filtA.append(vec1)
        vec2 = B[dictB[lhs_map[i]]]
        filtB.append(vec2)
        common.append(lhs_map[i])
    return np.array(filtA), np.array(filtB), common


def compute_cos_sim(A, B):
    """compute row-wise matrix similarity"""
    sim = []
    for i, row in enumerate(A):
        sim.append(1 - cosine(row, B[i]))
    return np.array(sim)


def compute_transform(A, B, orthogonal=False):
    if orthogonal:
        return compute_orthogonal_transform(A, B)
    else:
        return compute_nonorthogonal_transform(A, B)


def compute_nonorthogonal_transform(A, B):
    return np.linalg.pinv(A).dot(B)


def compute_orthogonal_transform(A, B):
    M = A.transpose().dot(B)
    U, S, V = np.linalg.svd(M)
    N = np.eye(U.shape[1], V.shape[0])
    return U.dot(N).dot(V)


def load_dictionary(fn):
    with open(fn) as f:
        return [l.decode('utf8').strip() for l in f]

def print_stats(dictionary, mtx, typ, mtx_from=None, mtx_to=None):
    if typ == 'cos':
        print_cos_similarities(dictionary, mtx)
    else:
        print_transform_similarities(dictionary, mtx, mtx_from, mtx_to)


def print_cos_similarities(dictionary, sim_mtx):
    for i, word in enumerate(dictionary):
        print(u'{0}\t{1}'.format(word, sim_mtx[i]).encode('utf8'))


def print_transform_similarities(dictionary, transform_mtx, mtx_from, mtx_to):
    for i, word in enumerate(dictionary):
        src = mtx_from[i]
        tgt = mtx_to[i]
        dist = 1 - cosine(transform_mtx.dot(src), tgt)
        print(u'{0}\t{1}'.format(word, dist).encode('utf8'))


def guess_dictname(mtx_fn, typ, dict_fn):
    if dict_fn:
        return dict_fn
    if typ == 'numpy':
        return '/'.join(mtx_fn.split('/')[:-1]) + '/dict.txt'
    return ""


def main():
    args = parse_args()
    left_dictionary = guess_dictname(args.matrix1, args.left_type, args.left_dictionary)
    right_dictionary = guess_dictname(args.matrix2, args.right_type, args.right_dictionary)
    m1, d1 = load_matrix_and_dictionary(args.matrix1, args.left_type, left_dictionary)
    m2, d2 = load_matrix_and_dictionary(args.matrix2, args.right_type, right_dictionary)
    m1, m2, common = filter_to_common_words(m1, m2, d1, d2)
    if args.type == 'cos':
        transform = compute_cos_sim(m1, m2)
    elif args.type == 'transform':
        transform = compute_transform(m1, m2, orthogonal=False)
    else:
        transform = compute_transform(m1, m2, orthogonal=True)
    if args.output:
        np.save(args.output, transform)
    print_stats(common, transform.transpose(), args.type, m1, m2)



if __name__ == '__main__':
    main()
