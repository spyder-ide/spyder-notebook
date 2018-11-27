#! /bin/bash -ex
# -e means:  Exit immediately if a command exits with a non-zero status
# -x means:  Print commands and their arguments as they are executed.

# Install some required system packages
sudo apt-get update
sudo apt-get install libegl1-mesa

# Install Miniconda
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda
source $HOME/miniconda/etc/profile.d/conda.sh

# Make new conda environment with required Python version
conda create -y -n test python=$PYTHON_VERSION
conda activate test

# Install Spyder's dependencies
conda install -y --only-deps spyder

# Download Spyder's source (3.x branch) from github 
mkdir spyder-source
pushd spyder-source
wget -q https://github.com/spyder-ide/spyder/archive/$SPYDER_BRANCH.zip
unzip -q $SPYDER_BRANCH.zip
popd

# Install Spyder from source
pushd spyder-source/spyder-$SPYDER_BRANCH
python setup.py install
popd

# Install spyder-notebook dependency
# Specify Qt 5 to prevent Qt 4 being installed with Python 2
conda install -y notebook qt=5

# Install testing dependencies
conda install -y pytest pytest-cov pytest-mock flaky
pip install coveralls pytest-qt

# List packages for debugging
echo '********** output of conda list **********'
conda list
