#! /bin/bash -ex
# -e means:  Exit immediately if a command exits with a non-zero status
# -x means:  Print commands and their arguments as they are executed.

source $HOME/miniconda/etc/profile.d/conda.sh
conda activate test

# Run tests; flag -x means stop on first test failure 
pytest -x -vv spyder_notebook --cov=spyder_notebook

# Generate coverage report
COVERALLS_REPO_TOKEN=Kr503QwklmJYKXYRXLywrtw8zbX7K8SKx coveralls
