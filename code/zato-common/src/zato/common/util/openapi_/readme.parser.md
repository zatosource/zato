# OpenAPI parser

This document explains how the `parser.py` module works.

## Data classes

There are two dataclasses:

### OpenAPIPathItem

```python
@dataclass(init=False)
class OpenAPIPathItem:
    name: str         # human-readable name from summary/operationId
    path: str         # the url path like /accounts/{id}
    auth: str         # "basic_auth", "oauth2", "api_key", or "unsupported-<name>"
    content_type: str # request content type, defaults to "application/json"
```

### OpenAPIDefinition

```python
@dataclass(init=False)
class OpenAPIDefinition:
    servers: list[str]            # list of server urls
    paths: list[OpenAPIPathItem]  # list of path items
```

## Parser class

The `Parser` class has two methods:

- `from_data(data: str) -> OpenAPIDefinition` - parses yaml/json string
- `from_url(url: str) -> OpenAPIDefinition` - downloads and parses from url

## How parsing works

1. Sanitizes non-printable characters (replaces with underscore, keeps newlines/tabs)
2. Tries yaml.safe_load first, falls back to json.loads
3. Extracts servers from `servers` list
4. Builds auth lookup from `components.securitySchemes`:
   - HTTP basic -> "basic_auth"
   - OAuth2 -> "oauth2"
   - API key -> "api_key"
   - anything else -> "unsupported-<scheme_name>"
5. Iterates over `paths`, creating an `OpenAPIPathItem` for each operation with:
   - auth from operation's `security` or global `security`
   - content_type from `requestBody.content` (first key, or "application/json")
   - name from `summary`, `operationId`, or generated from path
6. Fixes grammar ("a" -> "an" before vowels)
7. Returns `OpenAPIDefinition` containing list of servers and list of `OpenAPIPathItem` objects

## Examples from sample files

### DocuSign

Source yaml:
```yaml
openapi: 3.0.0
servers:
  - url: https://www.docusign.net/restapi
paths:
  /v2.1/accounts:
    post:
      summary: Creates new accounts.
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/newAccountDefinition'
```

Results in:
```
OpenAPIPathItem(
    name="Creates new accounts.",
    path="/v2.1/accounts",
    auth="",
    content_type="application/json"
)
```

No auth because DocuSign spec doesn't define securitySchemes in components.

### Open Banking

Source yaml:
```yaml
openapi: 3.0.0
paths:
  /account-access-consents:
    post:
      summary: Create Account Access Consents
      operationId: CreateAccountAccessConsents
      requestBody:
        content:
          application/json; charset=utf-8:
            schema:
              $ref: '#/components/schemas/OBReadConsent1'
      security:
        - TPPOAuth2Security:
            - accounts
```

Results in:
```
OpenAPIPathItem(
    name="Create Account Access Consents",
    path="/account-access-consents",
    auth="oauth2",
    content_type="application/json; charset=utf-8"
)
```

### TM Forum product catalog

Source yaml (swagger 2.0 format):
```yaml
basePath: /tmf-api/productCatalogManagement/v4/
paths:
  /catalog:
    get:
      summary: List or find Catalog objects
      operationId: listCatalog
    post:
      summary: Creates a Catalog
      operationId: createCatalog
      parameters:
        - in: body
          name: catalog
          required: true
          schema:
            $ref: '#/definitions/Catalog_Create'
```

Results in:
```
OpenAPIPathItem(
    name="List or find Catalog objects",
    path="/catalog",
    auth="",
    content_type="application/json"
)
OpenAPIPathItem(
    name="Creates a Catalog",
    path="/catalog",
    auth="",
    content_type="application/json"
)
```

Note: TM Forum uses swagger 2.0 which has `parameters` with `in: body` instead of `requestBody`. The parser defaults to "application/json" when no requestBody is found.

## Grammar fix

The parser fixes "a" -> "an" before vowels:
- "Creates a ExportJob" becomes "Creates an ExportJob"
- "Deletes a ImportJob" becomes "Deletes an ImportJob"

## Handling encoding issues

Some files (like DocuSign) contain non-printable characters that break yaml parsing. The parser sanitizes input by replacing non-printable characters (except newlines/tabs) with underscores before parsing.
