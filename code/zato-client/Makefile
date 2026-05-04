
.PHONY: test

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-client
PYTHON_BIN = python3

default: upload

upload3:
	$(MAKE) clean
	$(PYTHON_BIN) setup.py clean && $(PYTHON_BIN) setup.py bdist_wheel
	$(MAKE) twine

upload:
	$(MAKE) upload3

clean:
	rm -rf $(CURDIR)/dist/ && rm -rf $(CURDIR)/build

twine:
	twine upload $(CURDIR)/dist/*

ruff:
	echo "Running ruff in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/ruff check $(CURDIR)/
