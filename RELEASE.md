To release a new version of Spyder notebook on PyPI:

* Create an issue announcing the incoming release

* Close the respective milestone in GitHub

* git checkout master

* git fetch upstream && get merge upstream/master

* git clean -xfdi

* Update CHANGELOG.md with loghub

* Update `_version.py` (set release version, remove 'dev0')

* git add . && git commit -m 'Release X.X.X'

* python setup.py sdist upload

* python setup.py bdist_wheel upload

* git tag -a vX.X.X -m 'Release X.X.X'

* Update `_version.py` (add 'dev0' and increment minor)

* git add . && git commit -m 'Back to work'

* git push upstream master && git push upstream --tags

* Publish release announcement

* **Note**: Before using these commands be sure that the distribution is complete 
i.e all the needed files are in the tarball for uploading.
