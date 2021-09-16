VIRTUAL_ENV 	?= $(CURDIR)/env
PROJECT	   	?= marshmallow_peewee

all: $(VIRTUAL_ENV)

.PHONY: help
# target: help - Display callable targets
help:
	@egrep "^# target:" [Mm]akefile

# ==============
#  Bump version
# ==============

.PHONY: release
VERSION?=minor
# target: release - Bump version
release:
	@$(VIRTUAL_ENV)/bin/pip install bumpversion
	@$(VIRTUAL_ENV)/bin/bumpversion $(VERSION)
	@git checkout master
	@git merge develop
	@git checkout develop
	@git push origin develop master
	@git push --tags

.PHONY: minor
minor: release

.PHONY: patch
patch:
	make release VERSION=patch

.PHONY: major
major:
	make release VERSION=major

# ===============
#  Build package
# ===============

.PHONY: upload
# target: upload - Upload module on PyPi
upload: clean
	@$(VIRTUAL_ENV)/bin/pip install twine wheel
	@$(VIRTUAL_ENV)/bin/python setup.py sdist bdist_wheel
	@$(VIRTUAL_ENV)/bin/twine upload dist/*
	@$(VIRTUAL_ENV)/bin/pip install -e $(CURDIR)

# =============
#  Development
# =============

$(VIRTUAL_ENV): setup.cfg
	@[ -d $(VIRTUAL_ENV) ] || virtualenv --python=python3 $(VIRTUAL_ENV)
	@$(VIRTUAL_ENV)/bin/pip install -e .[tests]
	@touch $(VIRTUAL_ENV)

.PHONY: t test
# target: test - Run tests
t test: $(VIRTUAL_ENV)
	@$(VIRTUAL_ENV)/bin/pytest tests

.PHONY: mypy
# target: mypy - Run type checking
mypy: $(VIRTUAL_ENV)
	@$(VIRTUAL_ENV)/bin/mypy marshmallow_peewee
