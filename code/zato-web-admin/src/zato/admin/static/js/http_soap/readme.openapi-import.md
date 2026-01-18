# OpenAPI Import Frontend

This document explains how the OpenAPI import functionality works in the web admin frontend.

## Overview

The OpenAPI import allows users to paste an OpenAPI/Swagger specification and have it automatically create:
- Outgoing REST connections
- Security definitions (basic_auth, bearer_token)

## Files involved

- `openapi.js` - main JavaScript logic
- `openapi.css` - overlay styling
- `data-table-widget.js` - reusable table component
- `data-table-widget.css` - table styling
- `/zato/admin/web/views/openapi_.py` - backend views

## User flow

1. User clicks "Import OpenAPI" link on outgoing REST connections page
2. Tippy popup shows two options: "From copy/paste" or "From URL"
3. User clicks "From copy/paste"
4. Overlay appears with textarea containing sample OpenAPI YAML
5. User pastes their OpenAPI spec and clicks OK
6. Spinner shows "Reading ..." while parsing
7. Parser returns JSON with paths, auth info, servers
8. Table displays parsed paths with checkboxes (all checked by default)
9. User can filter, select/deselect items
10. User clicks OK to import
11. Spinner shows "Importing ..." while creating objects
12. Page reloads with green "OK, imported" message

## JavaScript functions

### `$.fn.zato.http_soap.openapi.init()`

Initializes the OpenAPI import functionality:
- Stores original textarea content for reset
- Checks for `openapi_imported=1` query param to show success message
- Sets up tippy popup on import link
- Binds event handlers for overlay buttons

### `$.fn.zato.http_soap.openapi.on_from_copy_paste()`

Shows the copy/paste overlay and focuses the textarea.

### `$.fn.zato.http_soap.openapi.on_copy_paste_ok()`

Called when user clicks OK on textarea view:
1. Shows "Reading ..." spinner
2. POSTs textarea content to `/zato/http-soap/openapi/parse/`
3. On success, calls `show_table()` with parsed data
4. On error, displays error message in textarea

### `$.fn.zato.http_soap.openapi.show_table(data)`

Transforms parsed OpenAPI data into table format:
```javascript
rows.push({
    name: path_item.name,
    path: path_item.path,
    server: server,              // first server from spec
    auth: path_item.auth,        // "basic_auth", "oauth2", etc.
    auth_server_url: path_item.auth_server_url,  // OAuth2 token URL
    content_type: path_item.content_type
});
```

Renders table using `$.fn.zato.data_table_widget.render()` with:
- Visible columns: Name, URL path
- Hidden fields: server, auth, auth_server_url, content_type, name, path

### `$.fn.zato.http_soap.openapi.on_table_import()`

Called when user clicks OK on table view:
1. Gets selected rows via `$.fn.zato.data_table_widget.get_selected()`
2. Shows "Importing ..." spinner
3. POSTs JSON array to `/zato/http-soap/openapi/import/`
4. On success, redirects to page with `?openapi_imported=1`

### `$.fn.zato.http_soap.openapi.show_spinner(message)`

Shows a centered spinner overlay with custom message text.

### `$.fn.zato.http_soap.openapi.close_copy_paste_overlay()`

Closes overlay, resets textarea to original content, hides table.

## Backend views

### `/zato/http-soap/openapi/parse/` (POST)

Receives raw OpenAPI YAML/JSON, invokes parser subprocess, returns JSON:
```json
{
    "success": true,
    "result": "{\"servers\": [...], \"paths\": [...]}"
}
```

### `/zato/http-soap/openapi/import/` (POST)

Receives array of selected items:
```json
[
    {
        "name": "Creates new accounts",
        "path": "/v2.1/accounts",
        "server": "https://api.example.com",
        "auth": "basic_auth",
        "auth_server_url": "",
        "content_type": "application/json"
    }
]
```

Calls `build_enmasse_config()` to generate YAML, then invokes `zato enmasse` CLI.

## Enmasse config generation

### `build_enmasse_config(items)`

Generates enmasse YAML structure:

```yaml
security:
  - name: openapi.basic_auth.Creates new accounts
    type: basic_auth
    username: basic_auth_user_creates_new_accounts
    password: <uuid4().hex>

  - name: openapi.oauth2.Gets users
    type: bearer_token
    username: bearer_token_user_gets_users
    password: <uuid4().hex>
    auth_server_url: https://example.com/oauth/token

outgoing_rest:
  - name: Creates new accounts
    host: https://api.example.com
    url_path: /v2.1/accounts
    data_format: json
    timeout: 600
    security: openapi.basic_auth.Creates new accounts
```

### Security type mapping

The `map_auth_to_security_type(auth)` function maps OpenAPI auth types:
- Contains "basic" → `basic_auth`
- Contains "bearer" or "oauth" → `bearer_token`
- Contains "api" and "key" → `apikey`
- Contains "ntlm" → `ntlm`
- Default → `basic_auth`

### Credentials generation

For each unique security definition:
- `username`: `{sec_type}_user_{name_with_underscores}`
- `password`: `uuid4().hex` (random 32-char hex string)
- `auth_server_url`: from OpenAPI spec's OAuth2 `tokenUrl` (for bearer_token only)

## Data table widget

### `$.fn.zato.data_table_widget.render(config)`

Renders a filterable, selectable table:
```javascript
{
    container_id: "openapi-data-table-container",
    columns: [{label: "Name", field: "name"}, ...],
    rows: [...],
    hidden_fields: ["server", "auth", ...],
    filter_placeholder: "Filter ..."
}
```

Features:
- Select-all checkbox in header
- Individual row checkboxes
- Click anywhere on row to toggle selection
- Filter input filters visible rows
- "No matches" message when filter yields no results
- All checkboxes checked by default on render

### `$.fn.zato.data_table_widget.get_selected(container_id, hidden_fields)`

Returns array of objects with hidden field values for all checked rows.

## Success message

After successful import:
1. Page redirects with `?openapi_imported=1` query param
2. `init()` detects param, removes it from URL via `replaceState`
3. Shows `#user-message-div` with green background
4. Flashes twice at 0.8s per flash via CSS animation
