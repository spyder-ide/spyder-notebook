#! /bin/bash -ex
# -e means:  Exit immediately if a command exits with a non-zero status
# -x means:  Print commands and their arguments as they are executed.

export PATH="$HOME/miniconda/bin:$PATH"
mkdir test-reports

# Run tests; flag -x means stop on first test failure 
pytest -x -vv spyder_notebook --cov=spyder_notebook --junitxml=test-reports/junit.xml

# Generate coverage report
COVERALLS_REPO_TOKEN=Kr503QwklmJYKXYRXLywrtw8zbX7K8SKx coveralls
