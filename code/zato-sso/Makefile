
.PHONY: build

PY_DIR=$(CURDIR)/../bin
Zato_Package_Name=zato-sso

run-tests:
	$(PY_DIR)/py $(CURDIR)/test/zato/test_command_line.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_user.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_session.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_user_attr_create.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_user_attr_update.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_user_attr_delete.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_user_attr_get.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_user_attr_exists.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_user_attr_names.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_session_attr_create.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_session_attr_update.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_session_attr_delete.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_session_attr_get.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_session_attr_exists.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_session_attr_names.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_session_list.py &&  \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_linked_auth.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_login_totp.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_password_reset.py

pylint:
	echo Running pylint in $(Zato_Package_Name)
	$(PY_DIR)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-sso/src/zato/sso

flake8:
	echo "Running flake8 checks in $(Zato_Package_Name)"
	$(PY_DIR)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

static-check:
	echo "Running static checks in $(Zato_Package_Name)"
	$(MAKE) flake8
