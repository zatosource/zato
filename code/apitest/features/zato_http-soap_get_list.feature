@http-soap
Feature: zato.http-soap.get-list
  Returns a list of plain HTTP or SOAP objects defined on a given cluster. These can be either channels or an outgoing connections.

## test plain_http list##
  @http-soap.get-list
  Scenario: Create JSON HTTP channel for zato.ping

      Given address "$ZATO_API_TEST_SERVER"
      Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

      Given URL path "/zato/json/zato.http-soap.create"

      Given format "JSON"
      Given request is "{}"
      Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
      Given JSON Pointer "/name" in request is a random string
      Given JSON Pointer "/is_active" in request is "true"
      Given JSON Pointer "/connection" in request is "channel"
      Given JSON Pointer "/transport" in request is "plain_http"
      Given JSON Pointer "/is_internal" in request is "false"
      Given JSON Pointer "/url_path" in request is "/apitest/httpcreate/test"
      Given JSON Pointer "/service" in request is "zato.ping"
      Given JSON Pointer "/data_format" in request is "json"

      When the URL is invoked

      Then status is "200"
      And I store "/zato_http_soap_create_response/name" from response under "service_channel_name"
      And I store "/zato_http_soap_create_response/id" from response under "service_channel_id"
      And I sleep for "1"

  @http-soap.get-list
  Scenario: Get plain_http channel list

    Given address "$ZATO_API_TEST_SERVER"

    Given URL path "/zato/json/zato.http-soap.get-list"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/connection" in request is "channel"
    Given JSON Pointer "/transport" in request is "plain_http"
    Given format "JSON"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_http_soap_get_list_response" isn't an empty list

  @http-soap.get-list
  Scenario: Delete created HTTP channel

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.http-soap.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#service_channel_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"


## test soap connection list ##
  @http-soap.get-list
  Scenario: Create HTTP channel for SOAP

      Given address "$ZATO_API_TEST_SERVER"
      Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

      Given URL path "/zato/json/zato.http-soap.create"

      Given format "JSON"
      Given request is "{}"
      Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
      Given JSON Pointer "/name" in request is a random string
      Given JSON Pointer "/is_active" in request is "true"
      Given JSON Pointer "/connection" in request is "channel"
      Given JSON Pointer "/transport" in request is "soap"
      Given JSON Pointer "/is_internal" in request is "false"
      Given JSON Pointer "/url_path" in request is "/apitest/soapcreate/test"
      Given JSON Pointer "/service" in request is "zato.ping"
      Given JSON Pointer "/data_format" in request is "xml"
      Given JSON Pointer "/soap_version" in request is "1.1"

      When the URL is invoked

      Then status is "200"
      And I store "/zato_http_soap_create_response/name" from response under "service_channel_name"
      And I store "/zato_http_soap_create_response/id" from response under "soap_channel_id"
      And I sleep for "1"

  @http-soap.get-list
  Scenario: Get soap channel list

    Given address "$ZATO_API_TEST_SERVER"

    Given URL path "/zato/json/zato.http-soap.get-list"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/connection" in request is "channel"
    Given JSON Pointer "/transport" in request is "soap"
    Given format "JSON"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_http_soap_get_list_response" isn't an empty list

  @http-soap.get-list
  Scenario: Delete created HTTP channel

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.http-soap.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#soap_channel_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"


## test outconn list##
  @http-soap.get-list
  Scenario: Create an outgoing HTTP connection which points to a dummy url

      Given address "$ZATO_API_TEST_SERVER"
      Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

      Given URL path "/zato/json/zato.http-soap.create"

      Given format "JSON"
      Given request is "{}"
      Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
      Given JSON Pointer "/name" in request is a random string
      Given JSON Pointer "/is_active" in request is "true"
      Given JSON Pointer "/connection" in request is "outgoing"
      Given JSON Pointer "/transport" in request is "plain_http"
      Given JSON Pointer "/is_internal" in request is "false"
      Given JSON Pointer "/url_path" in request is "/apitest/outconn/testlist"
      Given JSON Pointer "/host" in request is "$ZATO_API_TEST_SERVER"
      Given JSON Pointer "/data_format" in request is "json"
      Given JSON Pointer "/ping_method" in request is "HEAD"
      Given JSON Pointer "/pool_size" in request is "20"
      Given JSON Pointer "/timeout" in request is "10"

      When the URL is invoked

      Then status is "200"
      And I store "/zato_http_soap_create_response/name" from response under "outconn_name"
      And I store "/zato_http_soap_create_response/id" from response under "outconn_id"
      And I sleep for "1"

  @http-soap.get-list
  Scenario: Get outgoing connections channel list

    Given address "$ZATO_API_TEST_SERVER"

    Given URL path "/zato/json/zato.http-soap.get-list"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/connection" in request is "outgoing"
    Given JSON Pointer "/transport" in request is "plain_http"
    Given format "JSON"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON Pointer "/zato_http_soap_get_list_response" isn't an empty list

  @http-soap.get-list
  Scenario: Delete created HTTP channel

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.http-soap.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#outconn_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

