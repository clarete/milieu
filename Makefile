# Config
SHELL=bash
PACKAGE=milieu
TESTS_VERBOSITY=2

# UI colors
GREEN=\\033[0;32m
TITLE=\\033[0;35m
RESET=\\033[0m

# helpers
title=@echo -en "* $(TITLE)$(1): $(RESET)"
green=echo -e "$(GREEN)$(1)$(RESET)"
command=@$(1) 2>/tmp/.e 1>/tmp/.o; if [ \"\$\#\" == \"0\\" ]; then $(call green,ok); else cat /tmp/.e; fi
nose_command=@$(1) 2>/tmp/.e 1>/tmp/.o; if [ \"\$\#\" == \"0\\" ]; then $(call green,ok); cat /tmp/.{e,o}; else cat /tmp/.{e,o}; fi

# Default make rules
all: setup test
test: unit functional

# Test suites
unit: setup
	@make run_test suite=unit
functional: setup
	@make run_test suite=functional

# Install dependencies if we're inside of a virtualenv and the
# environment variable `SKIP_DEPS` is not set.
setup: clean
ifndef VIRTUAL_ENV
	$(error Cowardly refusing to run out of a virtualenv)
endif

ifndef SKIP_DEPS
	$(call title,"checking dependencies")
	$(call command,pip install -r development.txt)
endif

# Remove garbage from our working directory
clean:
	$(call title,"cleaning working directory")
	@find . -name '*.pyc' -delete
	@rm -rf .coverage *.egg-info *.log build dist MANIFEST
	@$(call green,ok)

# This is the most complicated part, the `run_test` rule takes the
# variable `suite` that is actually the folder name that will be
# executed. So the only possible values are `unit` and `functional`
# for now.
run_test:
ifneq "$(wildcard tests/$(suite))" ""
	$(call title,"running \'$(suite)\' tests")
	$(call nose_command,nosetests -v -s --force-color --stop \
		--with-coverage --cover-package=$(PACKAGE) --cover-branches --rednose \
		--verbosity=$(TESTS_VERBOSITY) tests/$(suite))
endif

# Run all the tests, update the version number and push the tarball to
# the pypi servers.
release: test
	$(call title,"uploading package to PyPi")
	@./.release
	@git push --tags
	@python setup.py sdist register upload
