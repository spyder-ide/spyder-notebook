# /bin/bash -e
# -e means:  Exit immediately if a command exits with a non-zero status

export PATH="$HOME/miniconda/bin:$PATH"
mkdir test-reports
pytest spyder_notebook --cov=spyder_notebook --junitxml=test-reports/junit.xml
COVERALLS_REPO_TOKEN=Kr503QwklmJYKXYRXLywrtw8zbX7K8SKx coveralls
