
.PHONY: default os-install install clean

MAKEFLAGS += --silent

DOTNET_DIR=$(CURDIR)
PUBLISH_DIR=$(DOTNET_DIR)/bin/publish
EXE=$(PUBLISH_DIR)/zato-hl7-interop

HOST ?= 127.0.0.1
PORT ?= 2575

default: $(EXE)
	$(EXE) $(HOST) $(PORT)

os-install:
	sudo apt-get update -qq
	sudo apt-get install -y dotnet-sdk-8.0

install:
	dotnet publish $(DOTNET_DIR)/ZatoHl7Interop.csproj \
		-c Release \
		-o $(PUBLISH_DIR) \
		--nologo \
		-v quiet

$(EXE): install

clean:
	rm -rf $(DOTNET_DIR)/bin $(DOTNET_DIR)/obj
