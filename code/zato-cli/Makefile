
.PHONY: ruff test

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-cli

test:
	$(Zato_Python_Dir)/py -m unittest discover -s $(CURDIR)/test/zato/enmasse_ -p 'test_*.py' -v

ruff:
	echo "Running ruff in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/ruff check $(CURDIR)/
