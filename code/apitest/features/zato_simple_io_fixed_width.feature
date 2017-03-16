
# ################################################################################################################################

@simple-io @fixed-width
Feature: SimpleIO FixedWidth
  SimpleIO tests for FixedWidth I/O

# ################################################################################################################################

  Scenario: FixedWidthString
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/checks/fixed-width/zato.checks.sio.fixed-width-string"

    Given format "RAW"
    Given request "fixed-width-string.txt"

    When the URL is invoked

    Then status is "200"
    And response is equal to "ab c  d   "

# ################################################################################################################################

  Scenario: FixedWidthStringMultiLine
    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/checks/fixed-width/zato.checks.sio.fixed-width-string-multi-line"

    Given format "RAW"
    Given request "fixed-width-string-multi-line.txt"

    When the URL is invoked

    Then status is "200"
    And response is equal to that from "fixed-width-string-multi-line.txt"

# ################################################################################################################################
