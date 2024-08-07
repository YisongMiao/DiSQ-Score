#!/bin/bash

# Please define your own path here
huggingface_path=YOUR_PATH

# Set the device number to 0 as a variable
device_number=0

# PDTB
for modelname in 7b 7bchat 13b 13bchat vicuna-13b
do
	for version in v1 v2 v3 v4
	do
		python scripts/question_answering.py --dataset pdtb --modelname $modelname --version $version --device_number $device_number --hfpath $huggingface_path
	done
done

# TED
for modelname in 7b 7bchat 13b 13bchat vicuna-13b
do
	for version in v1 v2 v3 v4
	do
		python scripts/question_answering.py --dataset ted --modelname $modelname --version $version --device_number $device_number --hfpath $huggingface_path
	done
done
