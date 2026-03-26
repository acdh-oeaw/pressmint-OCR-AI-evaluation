#!/bin/bash

#SBATCH --partition=g
#SBATCH --cpus-per-task=8
#SATCH  --mem=16G
#SBATCH --gres=gpu:A100:1
#SBATCH --time=06:00:00
#SBATCH --output=churro.log

title="churro__a100"

ntfy "${title} start"

echo "nproc"
nproc

echo "free h"
free -h

echo "nvidia-smi"
nvidia-smi

apptainer exec --fakeroot --containall --writable-tmpfs --nv \
  --bind ../../data/:/pressmint-ground-truth/data/ \
  --bind ./src/churro_transformers_infer.py:/pressmint-ground-truth/src/churro/src/churro_transformers_infer.py \
  --bind ./churro.sh:/pressmint-ground-truth/src/churro/churro.sh \
  churro.sif bash /pressmint-ground-truth/src/churro/churro.sh

ntfy "${title} done"

