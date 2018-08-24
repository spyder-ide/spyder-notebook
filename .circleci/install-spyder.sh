# /bin/bash -e
# -e means:  Exit immediately if a command exits with a non-zero status

export PATH="$HOME/miniconda/bin:$PATH"
conda install --only-deps spyder
mkdir spyder-source
cd spyder-source
wget -q https://github.com/spyder-ide/spyder/archive/3.x.zip
unzip -q 3.x.zip
cd spyder-3.x
python setup.py install
