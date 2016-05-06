#! /bin/sh
#
# compute_square_svd.sh
# Copyright (C) 2016 Judit Acs <judit@sch.bme.hu>
#
# Distributed under terms of the MIT license.
#


dimensions=( 10 30 300 )
dictionaries=( collins longman wiktionary )

for dim in "${dimensions[@]}"; do
    for dict in "${dictionaries[@]}"; do
        mkdir -p mtx/$dict/full_square/dim${dim}
        mkdir -p mtx/$dict/headword_square/dim${dim}
        nice -n 15 python src/decompose_definition_graph.py --definitions /mnt/store/home/judit/eval_dict/input/${dict}_firsts.json --dictionary mtx/${dict}/full_square/dim${dim}/dict.txt -k 30 --save-svd mtx/$dict/full_square/dim${dim}/ --square
        nice -n 15 python src/decompose_definition_graph.py --definitions /mnt/store/home/judit/eval_dict/input/${dict}_firsts.json --dictionary mtx/${dict}/headword_square/dim${dim}/dict.txt -k 30 --save-svd mtx/$dict/headword_square/dim${dim}/ --headword --square
    done
done

