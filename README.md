# Spyder notebook plugin

This is a Spyder plugin to use Jupyter notebooks inside Spyder. 
Currently it supports basic functionality such as creating new notebooks, opening any notebook in your filesystem and saving notebooks at any location.

You can also use Spyder's file switcher to easily switch between notebooks and open an IPython console connected to the kernel of a notebook to inspect its variables in the Variable Explorer.

## Project details

![license](https://img.shields.io/pypi/l/spyder-notebook.svg)
[![conda version](https://img.shields.io/conda/vn/conda-forge/spyder.svg)](https://anaconda.org/conda-forge/spyder)
[![download count](https://img.shields.io/conda/d/spyder-ide/spyder-notebook.svg)](https://www.anaconda.com/download/)
[![pypi version](https://img.shields.io/pypi/v/spyder-notebook.svg)](https://pypi.python.org/pypi/spyder-notebook)
[![OpenCollective Backers](https://opencollective.com/spyder/backers/badge.svg?color=blue)](#backers)
[![OpenCollective Sponsors](https://opencollective.com/spyder/sponsors/badge.svg?color=blue)](#sponsors) <br>
[![Tests](https://github.com/spyder-ide/spyder-notebook/actions/workflows/run-tests.yml/badge.svg)](https://github.com/spyder-ide/spyder/actions/workflows/run-tests.yml)
[![codecov](https://codecov.io/gh/spyder-ide/spyder-notebook/branch/master/graph/badge.svg)](https://codecov.io/gh/spyder-ide/spyder-notebook/branch/master)
[![Crowdin](https://badges.crowdin.net/spyder-notebook/localized.svg)](https://crowdin.com/project/spyder-notebook)


## Installation

This plugin can be installed using the ``conda`` package manager as follows:

```
conda install spyder-notebook -c conda-forge
```

The plugin is also available on PyPI. In principle, you can use `pip` to install it, but this often leads to installations that do not work properly.

**Note**: At the moment it is not possible to use this plugin with [Spyder's stand-alone installers](http://docs.spyder-ide.org/current/installation.html#standalone-installers). We're working to make that a reality in the future.

## Dependencies

This project depends on:

* [Spyder](https://github.com/spyder-ide/spyder)
* [Notebook](https://github.com/jupyter/notebook) from Jupyter

## Changelog
Visit our [CHANGELOG](CHANGELOG.md) file to know more about our new features and improvements.

## Development and contribution

See the 
[Contributing Guide](CONTRIBUTING.md)
for information on how to contribute to the Spyder notebook plugin, including
instructions for setting up a development environment.

## Contact

You can ask your questions at the [Spyder group](https://groups.google.com/forum/?utm_source=digest&utm_medium=email#!forum/spyderlib/topics)
or create a issue in this repo. We will be more than glad to answer.

## Overview
![example](https://raw.githubusercontent.com/spyder-ide/spyder-notebook/master/doc/example.gif)

## Sponsors

Spyder and its subprojects are funded thanks to the generous support of

[![Chan Zuckerberg Initiative](https://raw.githubusercontent.com/spyder-ide/spyder/master/img_src/czi.png)](https://chanzuckerberg.com/)[![Numfocus](https://i2.wp.com/numfocus.org/wp-content/uploads/2017/07/NumFocus_LRG.png?fit=320%2C148&ssl=1)](https://numfocus.org/)

and the donations we have received from our users around the world through [Open Collective](https://opencollective.com/spyder/):

[![Sponsors](https://opencollective.com/spyder/sponsors.svg)](https://opencollective.com/spyder#support)
