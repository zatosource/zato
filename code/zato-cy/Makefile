
.PHONY: build

default: clean

build:
	py $(CURDIR)/setup.py develop

clean:
	rm -rf $(CURDIR)/build
	find $(CURDIR) -type f -name '*.c' -delete
	find $(CURDIR) -type f -name '*.html' -delete
	find $(CURDIR) -type f -name '*.so' -delete
	find $(CURDIR) -name '*.egg-info' -exec rm -rf {} +

simpleio:
	py $(CURDIR)/setup.py develop && py $(CURDIR)/src/zato/cy/run_sio.py
