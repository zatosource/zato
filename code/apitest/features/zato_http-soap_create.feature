@http-soap
Feature: zato.http-soap.create
  Creates a new plain HTTP or SOAP object, this can be either channel or an outgoing connection, depending on the value of the ‘connection’ parameter.


  @http-soap.create
  Scenario: Set up
    Given I store "apitest.outconn" under "outconn_name"

### Test Create HTTP Connections that accept JSON ###

  @http-soap.create
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


  @http-soap.create
  Scenario: Invoke zato.ping through created http channel using JSON

    Given address "$ZATO_API_TEST_SERVER"

    Given URL path "/apitest/httpcreate/test"

    Given format "JSON"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"
    And JSON pointer "/zato_ping_response/pong" is "zato"


  @http-soap.create
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

### Test Create HTTP Connections that accept XML/SOAP ###

  @http-soap.create
  Scenario: Create HTTP channel for test-service.test-service SOAP

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

  @http-soap.create
  Scenario: Invoke zato.ping over created http channel using SOAP

    Given address "$ZATO_API_TEST_SERVER"

    Given URL path "/apitest/soapcreate/test"

    Given format "XML"
    Given request "security_wss_invoke_service.xml"
    Given namespace prefix "soapenv" of "http://schemas.xmlsoap.org/soap/envelope/"
    Given namespace prefix "zato" of "https://zato.io/ns/20130518"
    Given namespace prefix "wsse" of "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
    Given namespace prefix "wsu" of "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
    Given namespace prefix "soap" of "http://schemas.xmlsoap.org/soap/envelope/"

    When the URL is invoked

    Then status is "200"
    And XPath "//soap:Body/descendant::*[name()='result']" is "ZATO_OK"
    And XPath "//soap:Body/descendant::*[name()='pong']" is "zato"

  @http-soap.create
  Scenario: Delete created SOAP HTTP channel

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.http-soap.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#soap_channel_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

### Test Outgoing Connections ###

  @http-soap.create
  Scenario: Upload test_service

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.upload-package"

    Given format "JSON"
    Given request "service_upload.json"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"

    When the URL is invoked

    Then status is "200"
    And I sleep for "1"

  @http-soap.create
  Scenario: Create an HTTP endpoint for test service that will be called using an outgoing connection

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
      Given JSON Pointer "/url_path" in request is "/apitest/test-service"
      Given JSON Pointer "/service" in request is "test-service.test-service"
      Given JSON Pointer "/data_format" in request is "json"


      When the URL is invoked

      Then status is "200"
      And I store "/zato_http_soap_create_response/name" from response under "test_service_name"
      And I store "/zato_http_soap_create_response/id" from response under "test_service_id"
      And I sleep for "1"

  @http-soap.create
  Scenario: Upload outgoing_connection test service

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.upload-package"

    Given format "JSON"
    Given request "service_outconn_test.json"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"

    When the URL is invoked

    Then status is "200"
    And I sleep for "1"

  @http-soap.create
  Scenario: Create an HTTP endpoint to call the outgoing test service

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
      Given JSON Pointer "/url_path" in request is "/apitest/outgoing/invoke"
      Given JSON Pointer "/service" in request is "outcon-test-service.out-conn-test-service"
      Given JSON Pointer "/data_format" in request is "json"

      When the URL is invoked

      Then status is "200"
      And I store "/zato_http_soap_create_response/name" from response under "outconn_service_name"
      And I store "/zato_http_soap_create_response/id" from response under "outconn_service_id"
      And I sleep for "1"

  @http-soap.create
  Scenario: Create an outgoing HTTP connection which points to the test HTTP channel we created

      Given address "$ZATO_API_TEST_SERVER"
      Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

      Given URL path "/zato/json/zato.http-soap.create"

      Given format "JSON"
      Given request is "{}"
      Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
      Given JSON Pointer "/name" in request is "#outconn_name"
      Given JSON Pointer "/is_active" in request is "true"
      Given JSON Pointer "/connection" in request is "outgoing"
      Given JSON Pointer "/transport" in request is "plain_http"
      Given JSON Pointer "/is_internal" in request is "false"
      Given JSON Pointer "/url_path" in request is "/apitest/test-service"
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


  @http-soap.create
  Scenario: Call /apitest/outgoing/invoke HTTP endpoint which uses the outgoing connection to call the test service

    Given address "$ZATO_API_TEST_SERVER"
    Given URL path "/apitest/outgoing/invoke"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/service_request" in request is "hola outconn"

    When the URL is invoked

    Then status is "200"

    And JSON pointer "/response/test_service_response/service_response/echo_request" is "hola outconn"

  ### Outgoing connection ApiTest clean up ###
  @http-soap.create
  Scenario: Delete Outgoing connection

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.http-soap.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#outconn_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"


  @http-soap.create
  Scenario: Delete Outgoing HTTP Channel

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.http-soap.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#outconn_service_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"


  @http-soap.create
  Scenario: Delete Test Service HTTP Channel

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.http-soap.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#test_service_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

  #### Remove services ####
  @http-soap.create
  Scenario: Get outgoing service details by name

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.get-by-name"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "outcon-test-service.out-conn-test-service"
    When the URL is invoked

    Then status is "200"

    And I store "/zato_service_get_by_name_response/id" from response under "outconn_service_id"

  @http-soap.create
  Scenario: Delete Outgoing Test service

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#outconn_service_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

  @http-soap.create
  Scenario: Get test_service details by name

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.get-by-name"

    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/cluster_id" in request is "$ZATO_API_TEST_CLUSTER_ID"
    Given JSON Pointer "/name" in request is "test-service.test-service"
    When the URL is invoked

    Then status is "200"

    And I store "/zato_service_get_by_name_response/id" from response under "test_service_id"

  @http-soap.create
  Scenario: Delete test service

    Given address "$ZATO_API_TEST_SERVER"
    Given Basic Auth "$ZATO_API_TEST_PUBAPI_USER" "$ZATO_API_TEST_PUBAPI_PASSWORD"

    Given URL path "/zato/json/zato.service.delete"
    Given format "JSON"
    Given request is "{}"
    Given JSON Pointer "/id" in request is "#test_service_id"

    When the URL is invoked

    Then status is "200"
    And JSON Pointer "/zato_env/result" is "ZATO_OK"

### End test outgoing connections ###
