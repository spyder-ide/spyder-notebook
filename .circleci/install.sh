#! /bin/bash -ex
# -e means:  Exit immediately if a command exits with a non-zero status
# -x means:  Print commands and their arguments as they are executed.

# Install some required system packages
sudo apt-get update
sudo apt-get install libegl1-mesa

# Install Miniconda
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"

# Install required Python version
conda install -y python=$PYTHON_VERSION

# Install Spyder's dependencies
conda install -y --only-deps spyder

# Download Spyder's source (3.x branch) from github 
mkdir spyder-source
pushd spyder-source
wget -q https://github.com/spyder-ide/spyder/archive/3.x.zip
unzip -q 3.x.zip
popd

# Install Spyder from source
pushd spyder-source/spyder-3.x
python setup.py install
popd

# Install spyder-notebook dependency
conda install -y notebook

# Install testing dependencies
conda install -y pytest pytest-cov flaky
pip install coveralls pytest-qt

# Install spyder-notebook from source in developer mode
python setup.py develop

# List packages for debugging
echo '********** output of conda list **********'
conda list
