
.PHONY: ruff

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-distlock

test:
	echo "Running tests in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/distlock/test_*.py -s

ruff:
	echo "Running ruff in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/ruff check $(CURDIR)/
