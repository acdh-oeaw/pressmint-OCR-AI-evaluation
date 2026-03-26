#!/bin/bash

cd /pressmint-ground-truth/src/churro/src/
pixi run -e minimal python -u churro_transformers_infer.py

