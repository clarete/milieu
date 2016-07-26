all: setup test
test: unit functional
unit: setup; nosetests tests/unit
functional: setup; nosetests tests/functional

setup: clean
    ifndef VIRTUAL_ENV
	$(error Cowardly refusing to run out of a virtualenv)
    endif
    ifndef SKIP_DEPS
	echo "checking dependencies"
	pip install -r development.txt
    endif

clean:
	@echo "cleaning working directory"
	find . -name '*.pyc' -delete
	rm -rf .coverage *.egg-info *.log build dist MANIFEST

release: test
	@echo "uploading package to PyPi"
	git push --tags
	python setup.py sdist register upload
