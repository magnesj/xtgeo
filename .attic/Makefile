# =============================================================================
# Inherit values from ENV _or_ command line or use defaults for:
# $PYTHON_VERSION e.g. 2.7.13 (use current unless given)
# $PYTHON_SHORT e.g. 2.7 (optional)
# $PYTHON_VSHORT e.g. 2  (optional)
#
# e.g.
# > make install PYTHON_SHORT=2.7 PYTHON_VERSIONS=2.7.13
#
# or
# > setenv PYTHON_SHORT 2.7; setenv PYTHON_SHORT 2.7;
# > make install
#
# SDP special:
# $TARGET may also be applied explicitly for e.g. install at /project/res
# > setenv RESTARGET ${SDP_BINDIST_ROOT}/lib/python${PYTHON_SHORT}/site-packages
# > make sdpsiteinstall TARGET=$RESTARGET
#
# NEW:
# Instead of TARGET, the preferred method is now setting PREFIX instead:
# make siteinstall PREFIX=${SDP_BINDIST_ROOT}
#
# =============================================================================

xt.PHONY: clean clean-test clean-pyc clean-build clean-cc docs help pyver examples
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys
for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT


APPLICATION := xtgeo
DOCSINSTALL := /project/sdpdocs/XTGeo/libs

CXTGEOBUILD := src/xtgeo/cxtgeo/clib/build

BROWSER := firefox

PYTHON_VERSION ?= $(shell python -c "import sys; print('{0[0]}.{0[1]}.{0[2]}'.format(sys.version_info))")
PYTHON_SHORT ?= `echo ${PYTHON_VERSION} | cut -d. -f1,2`
PYTHON_VSHORT ?= `echo ${PYTHON_VERSION} | cut -d. -f1`

# Active python my be e.g. 'python3.4' or 'python3' (depends...)
ifeq (, python${PYTHON_SHORT})
PSHORT := ${PYTHON_SHORT}
else
PSHORT := ${PYTHON_VSHORT}
endif
PYTHON := python${PSHORT}
#PIP := pip${PSHORT}
PIP := ${PYTHON} -m pip

PREFIX := ${SDP_BINDIST_ROOT}
TARGET := ${PREFIX}/lib/python${PYTHON_SHORT}/site-packages
CUSTOM := ${HOME}

GID := res

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)


allclean: clean cclean  ## Cleanup all, both C compile stuff and Python


clean: clean-build clean-pyc clean-test clean-examples ## remove all Python build, test, coverage...


cclean: clean-cc ## remove all C compiling (CXTGeo) build


clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr tmp_buildswig/
	rm -fr dist/
	rm -fr wheel*/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +


clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +


clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr TMP/


clean-cc: ## remove C files and compiled files
	rm -fr ${CXTGEOBUILD}
	find . -name '*.so' -exec rm -f {} +
	find . -name '*.a' -exec rm -f {} +
	find . -name '*.dll' -exec rm -f {} +
	find . -name 'cxtgeo.py' -exec rm -fr {} +
	find . -name 'cxtgeo_wrap.c' -exec rm -fr {} +


clean-examples:
	find examples ! -name "*.py" ! -name "*.sh" -type f -exec rm -f {} +


lint: ## check style with pylint
	@${PYTHON} -m pylint ${APPLICATION} tests


flake: ## check style with flake8
	@${PYTHON} -m flake8 ${APPLICATION} tests


test:  ## run tests quickly with the default Python
	@${PYTHON} setup.py test


test-all: ## run tests on every Python version with tox (not active)
	tox


coverage: ## check code coverage quickly with the default Python
	coverage run --source ${APPLICATION} -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html


develop:  ## make develop mode (for pure python only)
	${PIP} install -e .


docsrun: develop ## generate Sphinx HTML documentation, including API docs
	rm -fr docs/apiref
	rm -fr docs/_build
	rm -fr docs/_static
	rm -fr docs/_templates
	# sphinx-apidoc -H "XTGeo API description" -o docs/ src/${APPLICATION}
	$(MAKE) -C docs clean
	$(MAKE) -C docs html


docs: docsrun ## generate and display Sphinx HTML documentation...
	$(BROWSER) docs/_build/html/index.html


examples: clean
	cd examples; ./runexamples.sh


servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .


dist: clean  ## builds wheel package
	@echo "Running ${PYTHON} (${PYTHON_VERSION}) bdist_wheel..."
	@${PYTHON} setup.py bdist_wheel


install: dist ## version to VENV install place
	@echo "Running ${PIP} (${PYTHON_VERSION}) ..."
	@${PIP} install --upgrade .


sdpsiteinstall: allclean dist ## Install in Equinor using $TARGET (old)
	@echo $(HOST)
	\rm -fr  ${TARGET}/${APPLICATION}
	\rm -fr  ${TARGET}/${APPLICATION}-*
	@${PIP} install --target ${TARGET} --upgrade  ./dist/${APPLICATION}*.whl


siteinstall: allclean dist ## Install to custom place using $PREFIX aka make siteinstall PREFIX=/local/usr
	@echo $(HOST)
	\rm -fr  ${PREFIX}/${APPLICATION}
	\rm -fr  ${PREFIX}/${APPLICATION}-*
	pip install --prefix=${PREFIX} .

userinstall: dist ## Install to user home folder (mostly for testing) using $CUSTOM
	PYTHONUSERBASE=${CUSTOM} ${PIP} install --upgrade --user .


docsinstall: docsrun  ## install docs in Equinor
	mkdir -p ${DOCSINSTALL}/${APPLICATION}
	rsync -av --delete docs/_build/html ${DOCSINSTALL}/${APPLICATION}
	/project/res/bin/res_perm ${DOCSINSTALL}/${APPLICATION}
