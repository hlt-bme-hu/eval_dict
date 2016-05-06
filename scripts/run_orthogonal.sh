#! /bin/sh
#
# run_orthogonal.sh
# Copyright (C) 2016 Judit Acs <judit@sch.bme.hu>
#
# Distributed under terms of the MIT license.
#


mtx_dir=mtx
resdir=results

dicts=( collins longman wiktionary )
dimensions=( 30 300 )
types=( headword full )

for dict1 in "${dicts[@]}"; do
    for dim1 in "${dimensions[@]}"; do
        for t1 in "${types[@]}"; do
            for dict2 in "${dicts[@]}"; do
                for dim2 in "${dimensions[@]}"; do
                    for t2 in "${types[@]}"; do
                        fn=$resdir/orthogonal/${dict1}_${t1}_${dim1}_${dict2}_${t2}_${dim2}
                        if [ ! -f $fn ]; then
                            echo $fn
                            python src/find_transform.py mtx/$dict1/$t1/dim${dim1}/US.mtx.npy mtx/$dict2/$t2/dim${dim2}/US.mtx.npy -t orthogonal | mean_std.py | tail -1 > $fn
                        fi
                    done
                done
            done

        done
    done

done


