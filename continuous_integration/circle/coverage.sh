#!/bin/bash

export COVERALLS_REPO_TOKEN=Kr503QwklmJYKXYRXLywrtw8zbX7K8SKx
source $HOME/miniconda/etc/profile.d/conda.sh
conda activate test

coveralls
