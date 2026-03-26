#!/bin/bash

./build_apptainer.sh
sbatch dots_ocr.sbatch

