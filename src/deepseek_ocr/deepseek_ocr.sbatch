#!/bin/bash

#SBATCH --partition=g
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --gres=gpu:A100:1
#SBATCH --time=01:00:00
#SBATCH --output=deepseek_ocr.log

title="deepseek_ocr"

ntfy "${title} start"

echo "nproc"
nproc

echo "free h"
free -h

echo "nvidia-smi"
nvidia-smi

apptainer exec --fakeroot --containall --nv --writable-tmpfs --bind ../../:/pressmint-ground-truth/ --bind ./root_home/:/root/ deepseek_ocr.sif bash /pressmint-ground-truth/src/deepseek_ocr/deepseek_ocr.sh

ntfy "${title} done"

