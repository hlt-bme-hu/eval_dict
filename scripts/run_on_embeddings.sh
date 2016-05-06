#! /bin/sh
#
# run_exps.sh
# Copyright (C) 2016 Judit Acs <judit@sch.bme.hu>
#
# Distributed under terms of the MIT license.
#

mtx_dir=mtx
outfile=results.txt
resdir=results2


w2v=( glove.42B.300d.w2v glove.6B.100d.w2v ) #glove.6B.200d.w2v glove.6B.300d.w2v glove.6B.50d.w2v glove.840B.300d.w2v GoogleNews-vectors-negative300-nocntrl.w2v GoogleNews-vectors-negative300.w2v hpca.2B.200d.w2v senna.w2v )
basedir=/mnt/store/home/hlt/Language/English/Embed
dicts=( collins longman wiktionary )
dimensions=( 30 300 )
types=( headword full )

for dict1 in "${dicts[@]}"; do
    for dim1 in "${dimensions[@]}"; do
        for t1 in "${types[@]}"; do
            for eb in "${w2v[@]}"; do
                emb=${basedir}/${eb}
                fn=$resdir/embedding/${dict1}_${t1}_${dim1}_${eb}
                if [ ! -f $fn ]; then
                    echo $fn
                    {( python src/find_transform.py mtx/$dict1/$t1/dim${dim1}/US.mtx.npy $emb --right-type word2vec | mean_std.py | tail -1 > $fn ) & }
                fi

                fn=$resdir/embedding/${eb}_${dict1}_${t1}_${dim1}
                if [ ! -f $fn ]; then
                    echo $fn
                    {( python src/find_transform.py $emb mtx/$dict1/$t1/dim${dim1}/US.mtx.npy --left-type word2vec | mean_std.py | tail -1 > $fn ) & }
                fi

                fn=$resdir/embedding_orthogonal/${eb}_${dict1}_${t1}_${dim1}
                if [ ! -f $fn ]; then
                    echo $fn
                    {( python src/find_transform.py -t orthogonal $emb mtx/$dict1/$t1/dim${dim1}/US.mtx.npy --left-type word2vec | mean_std.py | tail -1 > $fn ) & }
                fi
            done
        done
    done

done


