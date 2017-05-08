# Spyder notebook plugin

Spyder plugin for the use of notebooks inside Spyder,
using Jupyter Notebook. Currently it supports basic functionality as `New`,
`Open`, `Save As...`, and multiple notebooks open at once. Also, supports the use of the `find in files` functionality and the `file switcher` functionality.

**NOTE**

*This is a very (very!) crude implementation of the notebook running inside
Spyder as a plugin.*

*It won't be usable until we release the **0.1** version.*

## Build status

[![CircleCI](https://circleci.com/gh/spyder-ide/spyder-notebook.svg?style=svg)](https://circleci.com/gh/spyder-ide/spyder-notebook)
[![Coverage Status](https://coveralls.io/repos/github/spyder-ide/spyder-notebook/badge.svg?branch=master)](https://coveralls.io/github/spyder-ide/spyder-notebook?branch=master)

## Installation
To install this plugin, you can use either ``pip`` or ``conda`` package managers, as follows:

Using pip:
```
pip install spyder-notebook
```

Using conda:
```
conda install spyder-notebook
```

## Dependencies

This project depends on:

* [Spyder](https://github.com/spyder-ide/spyder) `>=3.1.4`
* [Notebook](https://github.com/jupyter/notebook) `>=4.3`


## Changelog
Visit our [CHANGELOG](CHANGELOG.md) file to know more about our new features and improvements.

## Development and contribution
To start contributing to this project you can execute ``python setup.py install`` to test your changes on Spyder. We follow PEP8 and PEP257 style guidelines.

# Overview
![example](/doc/example.gif)
