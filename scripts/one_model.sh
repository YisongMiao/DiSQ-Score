#!/bin/bash

# Check if modelurl argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <modelurl>"
    exit 1
fi

# Set the device number to 0 as a variable
device_number=3
# Get the model url from the first argument
modelurl=$1

# We first call the question generation bash (scripts/question_generation.py) script to generate the questions
bash scripts/question_generation.sh

# PDTB
for version in v1 v2 v3 v4
do
	python scripts/question_answering.py --dataset pdtb --modelurl $modelurl --version $version --device_number $device_number
done

# TED
for version in v1 v2 v3 v4
do
	python scripts/question_answering.py --dataset ted --modelurl $modelurl --version $version --device_number $device_number
done


for version in v1 v2 v3 v4
do
	python scripts/eval.py --dataset pdtb --version $version --modelurl $modelurl
done

python scripts/eval.py --dataset pdtb --version v4 --modelurl $modelurl --verbalize 1


for version in v1 v2 v3 v4
do
	python scripts/eval.py --dataset ted --version $version --modelurl $modelurl
done

python scripts/eval.py --dataset ted --version v4 --modelurl $modelurl --verbalize 1
