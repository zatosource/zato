
.PHONY: default os-install install clean test
MAKEFLAGS += --silent

JAVA_DIR=$(CURDIR)
SHADOW_JAR=$(JAVA_DIR)/build/libs/zato-hl7-interop-all.jar

HOST ?= 127.0.0.1
PORT ?= 2575

default: $(SHADOW_JAR)
	java -jar $(SHADOW_JAR) $(HOST) $(PORT)

os-install:
	sudo apt-get update -qq
	sudo apt-get install -y default-jdk-headless gradle

install: gradle-wrapper
	$(JAVA_DIR)/gradlew -p $(JAVA_DIR) shadowJar --no-daemon -q

gradle-wrapper:
	@if [ ! -f $(JAVA_DIR)/gradlew ]; then \
		echo "Generating Gradle wrapper ..."; \
		cd $(JAVA_DIR) && gradle wrapper --gradle-version 8.12 --no-daemon -q; \
	fi

$(SHADOW_JAR): install

test:
	$(JAVA_DIR)/gradlew -p $(JAVA_DIR) test --no-daemon

clean:
	rm -rf $(JAVA_DIR)/build $(JAVA_DIR)/.gradle
