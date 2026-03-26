#!/bin/bash

cd /pressmint-ground-truth/src/dots_ocr/src/
export PYTHONPATH=/pressmint-ground-truth/src/dots_ocr/src/

if [ ! -d ./weights/ ]; then
  python3 ./tools/download_model.py
fi

python3 ./demo/demo_hf.py

