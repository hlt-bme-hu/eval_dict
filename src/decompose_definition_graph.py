#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Judit Acs <judit@sch.bme.hu>
#
# Distributed under terms of the MIT license.

from argparse import ArgumentParser
import networkx as nx
import json
import logging
from os import path

import numpy as np
from scipy.sparse.linalg import svds
from scipy.sparse.csgraph import laplacian

from fourlang.dependency_processor import Dependencies

logging.getLogger().setLevel(logging.INFO)


def parse_args():
    p = ArgumentParser()
    p.add_argument('--definitions', help='defs json', type=str,
                   default='/home/recski/projects/4lang/data/dict/'
                   'collins_firsts_160204_readable.json')
    p.add_argument('-k', type=int, default=300)
    p.add_argument('--save-svd', type=str, default='svd')
    p.add_argument('--dictionary', type=str, default='dict.txt')
    p.add_argument('--laplacian-type', choices=['simple', 'normalized'],
                   default='simple')
    p.add_argument('--headword', action='store_true', default=False,
                   help='Build headword graph only')
    return p.parse_args()


class Graph(object):

    def __init__(self):
        self.graph = nx.DiGraph()
        self._expand_cache = {}

    def add_definition(self, lhs, rhs, headword_only=False):
        for sense in rhs['senses']:
            if not sense['definition']:
                continue
            for edge in sense['definition']['deps']:
                t = Dependencies.parse_dependency(edge)
                typ = t[0]
                src = t[1][0]
                tgt = t[2][0]
                if headword_only:
                    if typ == 'root':
                        self.graph.add_edge(lhs, tgt)
                else:
                    if not typ == 'root':
                        self.graph.add_edge(lhs, tgt)

    def expand_node(self, word, k=1):
        if word not in self._expand_cache:
            s = set(self.graph[word].keys())
            for _ in xrange(k):
                new_w = set()
                for w in s:
                    new_w |= set(self.graph[w].keys())
                s |= new_w
            self._expand_cache[word] = s
        return self._expand_cache[word]

    def compute_expand_jaccard(self, word1, word2):
        return Similarity.jaccard(
            self.expand_node(word1, k=1),
            self.expand_node(word2, k=1)
        )

    def compute_jaccard(self, word1, word2):
        if word1 not in self.graph:
            logging.warning('{} not in definition graph'.format(
                word1.encode('utf8')))
            return None
        if word2 not in self.graph:
            logging.warning('{} not in definition graph'.format(
                word2.encode('utf8')))
            return None
        return Similarity.jaccard(self.graph[word1].keys(),
                                  self.graph[word2].keys())

    def build_sim_graph(self, sim_func):
        sim = {}
        cnt = 0
        N = len(self.graph)
        for word1 in self.graph.nodes():
            cnt += 1
            if cnt % 1000 == 0:
                logging.info('{}/{}'.format(cnt, N))
            sim[word1] = {}
            for word2 in self.graph.successors(word1):
                for word3 in self.graph.predecessors(word2):
                    if word1 > word3:
                        continue
                    if word3 in sim[word1]:
                        continue
                    s = sim_func(word1, word3)
                    sim[word1][word3] = s
        return sim

    def save_matrix(self, sim, fn):
        with open(fn, 'w') as f:
            for w1, words in sorted(sim.iteritems(), key=lambda x: x[0]):
                for w2, sim in sorted(words.iteritems(), key=lambda x: x[0]):
                    f.write('{0}\t{1}\t{2}\n'.format(w1, w2, sim))

    def compute_laplacian(self, laplacian_type='simple'):
        am = nx.adjacency_matrix(self.graph)
        if laplacian_type == 'simple':
            return laplacian(am).asfptype()
        elif laplacian_type == 'normalized':
            return laplacian(am, normed=True).asfptype()
        raise Exception('Unknown Laplacian type: {}'.format(laplacian_type))

    def compute_svd(self, k, laplacian_type='simple'):
        lp = self.compute_laplacian(laplacian_type)
        U, S, V = svds(lp, k=k)
        self.U = U
        self.S = np.diag(S)
        self.V = V

    def save_svd(self, prefix):
        np.save(path.join(prefix, 'U.mtx'), self.U)
        np.save(path.join(prefix, 'S.mtx'), self.S)
        np.save(path.join(prefix, 'V.mtx'), self.V)
        np.save(path.join(prefix, 'US.mtx'), self.U.dot(self.S))

    def save_dictionary(self, fn):
        with open(fn, 'w') as f:
            f.write('\n'.join(self.graph.nodes()).encode('utf8'))


class Similarity(object):

    @staticmethod
    def jaccard(s1, s2):
        set1 = set(s1)
        set2 = set(s2)
        if not set1 and not set2:
            return 0
        return float(len(set1 & set2)) / len(set1 | set2)


def build_graph(fn, headword_only=False):
    if fn.endswith('.json'):
        return build_graph_from_json(fn, headword_only)
    return build_graph_from_tsv(fn)


def build_graph_from_json(fn, headword_only):
    with open(fn) as f:
        d = json.load(f)
        graph = Graph()
        for lhs, rhs in d.iteritems():
            graph.add_definition(lhs, rhs, headword_only)
        return graph


def build_graph_from_tsv(fn):
    with open(fn) as f:
        graph = Graph()
        for l in f:
            lhs, rhs = l.decode('utf8').strip().split('\t')
            for word in rhs.split():
                graph.graph.add_edge(lhs, word)
        return graph


def main():
    args = parse_args()
    g = build_graph(args.definitions, args.headword)
    logging.info("Definition graph loaded")
    g.compute_svd(k=args.k, laplacian_type=args.laplacian_type)
    logging.info("SVD finished")
    g.save_svd(prefix=args.save_svd)
    g.save_dictionary(args.dictionary)

if __name__ == '__main__':
    main()
