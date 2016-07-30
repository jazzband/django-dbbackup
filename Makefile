.PHONY: all test clean docs

clean:
	find . -name "*.pyc" -type f -delete
	find . -name "__pycache__" -type d -exec rm -rf {} \;
	find . -name "*.egg-info" -type d -exec rm -rf {} \; || true
	rm -rf build/ dist/ \
	       coverage_html_report .coverage \
	       *.egg

test:
	python runtests.py

install:
	python setup.py install

build:
	python setup.py build

docs:
	cd docs/ && make clean
	cd docs/ && make html

upload:
	make clean
	python setup.py sdist bdist_wheel
	twine upload dist/*
