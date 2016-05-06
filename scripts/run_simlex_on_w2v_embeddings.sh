#! /bin/sh
#
# run_exps.sh
# Copyright (C) 2016 Judit Acs <judit@sch.bme.hu>
#
# Distributed under terms of the MIT license.
#


resdir=results
basedir=/mnt/store/home/hlt/Language/English/Embed
w2v=( glove.42B.300d.w2v glove.6B.100d.w2v glove.6B.200d.w2v glove.6B.300d.w2v glove.6B.50d.w2v glove.840B.300d.w2v GoogleNews-vectors-negative300-nocntrl.w2v GoogleNews-vectors-negative300.w2v hpca.2B.200d.w2v senna.w2v )

for emb in "${w2v[@]}"; do
    echo $emb
    fn=${basedir}/${emb}
    outfn=$resdir/simlex/${emb}
    tail -n +2 $fn > /tmp/judit/glove_format.txt
    if [ ! -f $outfn ]; then

        cat /mnt/store/home/hlt/wordsim/sim_data/simlex/SimLex-999.txt | python /mnt/store/hlt/Work/DSALT/scripts/simlex.py /tmp/judit/glove_format.txt 2>>/tmp/judit/err | tail -2 > ${outfn}
    fi
done

rm /tmp/judit/glove_format.txt


