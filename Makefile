checkfiles = digicubes_rest/

help:
	@echo  "DigiCubes platform development makefile"
	@echo
	@echo  "usage: make <target>"
	@echo  "Targets:"
	@echo  "    up      Updates dev/test dependencies"
	@echo  "    deps    Ensure dev/test dependencies are installed for development"
	@echo  "    lint	Reports all linter violations"

up:
	@pip install -q pip-tools
	CUSTOM_COMPILE_COMMAND="make up" pip-compile -o requirements.txt requirements.in -U
	CUSTOM_COMPILE_COMMAND="make up" pip-compile -o requirements-dev.txt requirements-dev.in -U

tapi: export DIGICUBES_CONFIG_FILE=configuration.yaml
tapi: export DIGICUBES_CONFIG_PATH=cfg

api:
	python rundigicubes.py

deps:
	@pip install -q pip-tools
	@pip install -q wheel
	@pip-sync requirements-dev.txt

lint: deps
	pylint $(checkfiles)

schema: deps
	rm -f *.db*
	python create_schema.py

checkdocs:
	doc8 source/

docs:
	sphinx-build -E -b html source build
	sphinx-build -E -b html source_client build_client

ci:	check
	pylint --errors-only $(checkfiles)
	nose2 -v digicubes

nose: deps
	nose2 -v digicubes

check: deps
	black -l 100 --check $(checkfiles)

style:
	black -l 100 $(checkfiles) 

badges: deps
	python lintbadge.py

build: ci
	rm -fR dist/
	#python setup_client.py sdist bdist_wheel
	python setup.py sdist bdist_wheel

publish: build
	twine check ./dist/*
	twine upload ./dist/*

docker-build:
	docker build -t digicubes-server .
