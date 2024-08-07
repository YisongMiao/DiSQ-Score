#!/bin/bash

for modelname in 7b 7bchat 13b 13bchat vicuna-13b
do
	for version in v1 v2 v3 v4
	do
		python scripts/eval.py --dataset pdtb --modelname $modelname --version $version
	done
done

for modelname in 7b 7bchat 13b 13bchat vicuna-13b
do
	for version in v1 v2 v3 v4
	do
		python scripts/eval.py --dataset ted --modelname $modelname --version $version
	done
done
