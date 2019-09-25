#!/bin/bash -ex

# -- Install Miniconda
MINICONDA=Miniconda3-latest-Linux-x86_64.sh
wget https://repo.continuum.io/miniconda/$MINICONDA -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda
source $HOME/miniconda/etc/profile.d/conda.sh


# -- Make new conda environment with required Python version
conda create -y -n test python=$PYTHON_VERSION
conda activate test


# -- Install dependencies

# Avoid problems with invalid SSL certificates
if [ "$PYTHON_VERSION" = "2.7" ]; then
    conda install -q -y python=2.7.16=h9bab390_0
fi

# Install nomkl to avoid installing Intel MKL libraries
conda install -q -y nomkl

# Install main dependencies
conda install -q -y -c spyder-ide --file requirements/conda.txt

# Install test ones
conda install -q -y -c spyder-ide --file requirements/tests.txt
