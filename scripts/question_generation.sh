#!/bin/bash

# generate for dataset PDTB with version v1 to v4
for version in v1 v2 v3 v4
do
	python scripts/question_generation.py --dataset pdtb --version $version
done

# generate for dataset TED with version v1 to v4
for version in v1 v2 v3 v4
do
	python scripts/question_generation.py --dataset ted --version $version
done
