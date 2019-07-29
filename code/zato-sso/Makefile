
.PHONY: build

sso-test:
	py $(CURDIR)/test/zato/test_user.py && \
	py $(CURDIR)/test/zato/test_session.py && \
	py $(CURDIR)/test/zato/test_user_attr_create.py && \
	py $(CURDIR)/test/zato/test_user_attr_update.py && \
	py $(CURDIR)/test/zato/test_user_attr_delete.py && \
	py $(CURDIR)/test/zato/test_user_attr_get.py && \
	py $(CURDIR)/test/zato/test_user_attr_exists.py && \
	py $(CURDIR)/test/zato/test_user_attr_names.py && \
	py $(CURDIR)/test/zato/test_session_attr_create.py && \
	py $(CURDIR)/test/zato/test_session_attr_update.py && \
	py $(CURDIR)/test/zato/test_session_attr_delete.py && \
	py $(CURDIR)/test/zato/test_session_attr_get.py && \
	py $(CURDIR)/test/zato/test_session_attr_exists.py && \
	py $(CURDIR)/test/zato/test_session_attr_names.py && \
	py $(CURDIR)/test/zato/test_session_list.py &&  \
	py $(CURDIR)/test/zato/test_linked_auth.py && \
	py $(CURDIR)/test/zato/test_login_totp.py
