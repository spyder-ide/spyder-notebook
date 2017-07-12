# Spyder notebook plugin

Spyder plugin to use Jupyter notebooks inside Spyder. Currently it supports
basic functionality such as creating new notebooks, opening any notebook in
your filesystem and saving notebooks at any location.

You can also use Spyder's file switcher to easily switch between notebooks
and open an IPython console connected to the kernel of a notebook to inspect
its variables in the Variable Explorer.

## Build status

[![CircleCI](https://circleci.com/gh/spyder-ide/spyder-notebook.svg?style=svg)](https://circleci.com/gh/spyder-ide/spyder-notebook)
[![Coverage Status](https://coveralls.io/repos/github/spyder-ide/spyder-notebook/badge.svg?branch=master)](https://coveralls.io/github/spyder-ide/spyder-notebook?branch=master)

## Installation

To install this plugin, you can use either ``pip`` or ``conda`` package managers, as follows:

Using conda (the recommended way!):

```
conda install spyder-notebook -c spyder-ide
```

Using pip:

```
pip install spyder-notebook
```

## Dependencies

This project depends on:

* [Spyder](https://github.com/spyder-ide/spyder) `>=3.2`
* [Notebook](https://github.com/jupyter/notebook) `>=4.3`


## Changelog
Visit our [CHANGELOG](CHANGELOG.md) file to know more about our new features and improvements.

## Development and contribution
To start contributing to this project you can execute ``python setup.py install`` to test your changes on Spyder. We follow PEP8 and PEP257 style guidelines.

# Overview
![example](/doc/example.gif)
