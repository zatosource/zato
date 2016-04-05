
Feature: zato.http-soap.create.*

    @http-soap
    Scenario: Set up

        Given I store a random string under "url_path"
        Given I store a random string under "basic_username"
        Given I store a random string under "basic_password"
        Given I store a random string under "new_password"