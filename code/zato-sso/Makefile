
.PHONY: build

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-sso

run-tests:
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_command_line.py && \
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_user.py && \
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_session.py && \
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_user_attr_create.py && \
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_user_attr_update.py && \
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_user_attr_delete.py && \
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_user_attr_get.py && \
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_user_attr_exists.py && \
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_user_attr_names.py && \
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_session_attr_create.py && \
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_session_attr_update.py && \
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_session_attr_delete.py && \
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_session_attr_get.py && \
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_session_attr_exists.py && \
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_session_attr_names.py && \
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_session_list.py &&  \
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_linked_auth.py && \
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_login_totp.py && \
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_password_reset.py

pylint:
	echo Running pylint in $(Zato_Package_Name)
	$(Zato_Python_Dir)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-sso/src/zato/sso

mypy:
	$(Zato_Python_Dir)/mypy --config-file=$(CURDIR)/../mypy.ini \
			$(CURDIR)/src/zato/sso/*.py

pyright:
	$(Zato_Python_Dir)/pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/sso/*.py

type-check:
	echo "Running type checks ($(Zato_Package_Name))"
	# $(MAKE) mypy
	# $(MAKE) pyright

flake8:
	echo "Running flake8 checks in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

static-check:
	echo "Running static checks in $(Zato_Package_Name)"
	$(MAKE) flake8
	$(MAKE) type-check
