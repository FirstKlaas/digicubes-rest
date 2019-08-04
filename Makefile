checkfiles = digicubes/ create_schema.py

help:
	@echo  "Digicubes platform development makefile"
	@echo
	@echo  "usage: make <target>"
	@echo  "Targets:"
	@echo  "    up      Updates dev/test dependencies"
	@echo  "    deps    Ensure dev/test dependencies are installed for development"
	@echo  "    lint	Reports all linter violations"

up:
	@pip install -q pip-tools
	CUSTOM_COMPILE_COMMAND="make up" pip-compile -o requirements.txt requirements.in -U
	CUSTOM_COMPILE_COMMAND="make up" pip-compile -o requirements_client.txt requirements_client.in -U
	CUSTOM_COMPILE_COMMAND="make up" pip-compile -o requirements-dev.txt requirements-dev.in -U


deps:
	@pip install -q pip-tools
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

nose:
	nose2 -v digicubes

check:
	black -l 100 --check digicubes/

style:
	black -l 100 digicubes/ 

badges: deps
	python lintbadge.py

wsldocs: docs
	cp -a build/ /mnt/c/Users/nebuhr/Documents/Privat/
	cp -a build_client/ /mnt/c/Users/nebuhr/Documents/Privat/
