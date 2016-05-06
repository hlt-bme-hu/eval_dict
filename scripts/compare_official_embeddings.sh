#! /bin/sh
#
# run_exps.sh
# Copyright (C) 2016 Judit Acs <judit@sch.bme.hu>
#
# Distributed under terms of the MIT license.
#

resdir=results

w2v=( glove.42B.300d.w2v glove.6B.100d.w2v glove.6B.200d.w2v glove.6B.300d.w2v glove.6B.50d.w2v glove.840B.300d.w2v GoogleNews-vectors-negative300-nocntrl.w2v GoogleNews-vectors-negative300.w2v hpca.2B.200d.w2v senna.w2v )
basedir=/mnt/store/home/hlt/Language/English/Embed

for emb1 in "${w2v[@]}"; do
    fn1=${basedir}/${emb1}
    for emb2 in "${w2v[@]}"; do
        if [ ! "$emb1" \> "$emb2" ]; then
            echo $emb1 $emb2
            fn2=${basedir}/${emb1}
            outfn=$resdir/embedding/${emb1}_${emb2}
            if [ ! -f $outfn ]; then
                echo $outfn
                python src/find_transform.py $fn1 $fn2 --left-type word2vec --right-type word2vec | mean_std.py | tail -1 > $outfn
            fi
            outfn=$resdir/embedding/${emb2}_${emb1}
            if [ ! -f $outfn ]; then
                echo $outfn
                python src/find_transform.py $fn2 $fn1 --left-type word2vec --right-type word2vec | mean_std.py | tail -1 > $outfn
            fi

            outfn=$resdir/embedding_orthogonal/${emb1}_${emb2}
            if [ ! -f $outfn ]; then
                echo $outfn
                python src/find_transform.py $fn1 $fn2 --left-type word2vec --right-type word2vec | mean_std.py | tail -1 > $outfn
            fi
        fi
    done
done


