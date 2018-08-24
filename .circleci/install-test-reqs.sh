# /bin/bash -e
# -e means:  Exit immediately if a command exits with a non-zero status

export PATH="$HOME/miniconda/bin:$PATH"
conda install -q notebook pytest pytest-cov flaky
pip install coveralls pytest-qt
python setup.py develop
echo '********** output of conda list **********'
conda list
