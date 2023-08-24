# Contributing to the Spyder notebook plugin

:+1::tada: 
First off, thanks for taking the time to contribute to the Spyder notebook
plugin! 
:tada::+1:

## General guidelines for contributing

The Spyder notebook plugin is developed as part of the wider Spyder project.
In general, the guidelines for contributing to Spyder also apply here.
Specifically, all contributors are expected to abide by
[Spyder's Code of Conduct](https://github.com/spyder-ide/spyder/blob/master/CODE_OF_CONDUCT.md).

There are many ways to contribute and all are valued and welcome. 
You can help other users, write documentation, spread the word, submit
helpful issues on the
[issue tracker](https://github.com/spyder-ide/spyder-notebook/issues)
with problems you encounter or ways to improve the plugin, test the development
version, or submit a pull request on GitHub.

The rest of this document explains how to set up a development environment.

## Setting up a development environment

This section explains how to set up a conda environment to run and work on the
development version of the Spyder notebook plugin.

### Creating a conda environment

This creates a new conda environment with the name `spydernb-dev`.

```bash
$ conda create -n spydernb-dev python
$ conda activate spydernb-dev
```

### Cloning the repository

This creates a new directory `spyder-notebook` with the source code of the
Spyder notebook plugin.

```bash
$ git clone https://github.com/spyder-ide/spyder-notebook.git
$ cd spyder-notebook
```

### Installing dependencies

This installs Spyder, JupyterLab and all other dependencies of the plugin into
the conda environment.

```bash
$ conda install --file requirements/conda.txt
```

### Building the notebook server

The Spyder notebook plugin includes a server which serves notebooks as HTML
pages. The following commands install the JavaScript dependencies of the
notebook server and build the server.

```bash
$ conda install nodejs
$ cd spyder_notebook/server
$ jlpm install
$ jlpm build
$ cd ../..
```

### Installing the plugin

This installs the Spyder notebook plugin so that Spyder will use it.

```bash
$ pip install --no-deps -e .
```

### Running Spyder

You are done! You can run Spyder as normal and it should load the notebook
plugin.

```bash
$ spyder
```

### Running Tests

This command installs the test dependencies in the conda environment.

```bash
$ conda install -c spyder-ide --file requirements/tests.txt
```

You can now run the tests with a simple

```bash
$ pytest
```
