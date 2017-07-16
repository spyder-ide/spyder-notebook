To release a new version of Spyder notebook on PyPI:

* git fetch upstream && get merge upstream/master

* Update CHANGELOG.md with loghub

* Update `_version.py` (set release version, remove 'dev0')

* git add and git commit

* python setup.py sdist upload

* python setup.py bdist_wheel upload

* git tag -a vX.X.X -m 'Release X.X.X'

* Update `_version.py` (add 'dev0' and increment minor)

* git add and git commit

* git push

* git push --tags