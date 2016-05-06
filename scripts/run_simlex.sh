#! /bin/sh
#
# run_simlex.sh
# Copyright (C) 2016 Judit Acs <judit@sch.bme.hu>
#
# Distributed under terms of the MIT license.
#


resdir=results

glove=( /mnt/store/hlt/Work/DSALT/data/vectors.1.riffle.txt /mnt/store/hlt/Work/DSALT/data/vectors.2.riffle.txt )
dicts=( collins longman wiktionary )
dimensions=( 30 300 )
types=( headword full )

for dict1 in "${dicts[@]}"; do
    for dim1 in "${dimensions[@]}"; do
        for t1 in "${types[@]}"; do
            fn=$resdir/simlex/${dict1}_${t1}_${dim1}
            if [ ! -f $fn ]; then
                echo $fn
                python src/convert_embedding.py -i mtx/$dict1/$t1/dim${dim1}/US.mtx.npy -d mtx/$dict1/$t1/dim${dim1}/dict.txt -o /tmp/judit/glove_format.txt
                cat /mnt/store/home/hlt/wordsim/sim_data/simlex/SimLex-999.txt | python /mnt/store/hlt/Work/DSALT/scripts/simlex.py /tmp/judit/glove_format.txt 2>>/tmp/judit/err | tail -2 > ${fn}
            fi
        done
    done

done


