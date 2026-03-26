#!/bin/bash

#SBATCH --partition=g
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --gres=gpu:A100:1
#SBATCH --time=05:00:00
#SBATCH --output=dots_ocr.log

title="dots_ocr"

ntfy "${title} start"

echo "nproc"
nproc

echo "free h"
free -h

echo "nvidia-smi"
nvidia-smi

apptainer exec --fakeroot --containall --writable-tmpfs --nv \
  --bind ../../data/:/pressmint-ground-truth/data/ \
  --bind ./src/demo/demo_hf.py:/pressmint-ground-truth/src/dots_ocr/src/demo/demo_hf.py \
  --bind ./dots_ocr.sh:/pressmint-ground-truth/src/dots_ocr/dots_ocr.sh \
  dots_ocr.sif bash /pressmint-ground-truth/src/dots_ocr/dots_ocr.sh

ntfy "${title} done"

