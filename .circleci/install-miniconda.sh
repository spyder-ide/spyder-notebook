# /bin/bash -e
# -e means:  Exit immediately if a command exits with a non-zero status

wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
conda install python=$PYTHON_VERSION
