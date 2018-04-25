test_args?=-v

test:
	./runtests.py $(test_args)

build:
	python setup.py sdist bdist_wheel

upload:
	twine upload dist/*

uploadtest:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

clean:
	rm -fr dist build *.egg-info .tox
