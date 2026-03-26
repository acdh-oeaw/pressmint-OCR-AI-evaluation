#!/bin/bash

#SBATCH --partition=g
#SBATCH --cpus-per-task=16
#SATCH  --mem=64G
#SBATCH --gres=gpu:A100:1
#SBATCH --time=03:00:00
#SBATCH --output=dots_ocr.log

title="dots_ocr__a100"

ntfy "${title} start"

echo "nproc"
nproc

echo "free h"
free -h

echo "nvidia-smi"
nvidia-smi

apptainer exec --bind ../../:/pressmint-ground-truth/ --nv --writable-tmpfs dots_ocr.sif bash /pressmint-ground-truth/src/dots_ocr/dots_ocr.sh

ntfy "${title} done"

