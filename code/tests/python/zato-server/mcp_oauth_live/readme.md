# OAuth for MCP gateways - the live suite and the checklist for real clients

The modules in this directory simulate what each AI client product does when it connects to a gateway with OAuth
on - the probe, the metadata, the browser sign-in with PKCE, the token on every request - against the
`zato-test-keycloak` container and a Zato server the session fixture starts. They prove the gateway conforms to what
each product's documentation says. The checklist below is for the runs that prove the products do too, with
the real client in hand, and each run is one row.

## Running the suite

The Keycloak container is created and provisioned by `zato-common/test/keycloak_.py` on first use, with
`keycloak_oauth.py` adding the people, the group, the public clients and the open client registration this suite
needs. The Zato server comes from `live_environment/quickstart.py` on a free port. Nothing here binds a fixed port
of its own.

```
make test-mcp-oauth
```

One module per product - `test_vscode.py`, `test_cursor.py`, `test_claude_code.py`, `test_claude_ai.py` and
`test_chatgpt.py` - each a `ClientProfile` and a subclass of `ClientSuite` from `_steps.py`, which holds every step
the products share. `test_isolation.py` covers what is not about one product - a gateway with OAuth off next to one
with it on, two people on one definition, and the alert about rejected callers.

## What a manual run consists of

The gateway is any gateway with OAuth on whose group holds a bearer definition with the issuer and the audience of
the identity provider below, `identity_claim: preferred_username` and `claims: [groups=billing-agents]`, with its
audit log on. Two accounts exist at the provider - Maria Johnson in the `billing-agents` group and John Smith in no
group. A run of one row is these steps, in order, and the row is checked when every step held:

1. Connect the product to the gateway the way its page under `docs/ai/mcp/clients/` says, with the client ID of the
   registration made for it, or with no client ID for a product that registers itself.
2. Sign in as Maria. The product lists the gateway's tools and a tool call returns its result.
3. In the gateway's audit log, the `mcp-tools-call` event names Maria in the Identity column, the product's client
   ID in the Client column and `groups=billing-agents` under `claims_matched`.
4. Sign out, or remove the connection, and connect again as John. The product reports that the server refused the
   credentials and offers the sign-in again.
5. In the audit log, the `auth-failed` event names John in the Identity column and `claim_missing` in the Reason
   column.

## Against Keycloak

The realm is the one `keycloak_oauth.py` provisions, with the public clients and the redirect URIs it registers,
so the client IDs are the `Client_*` constants of that module. ChatGPT registers itself through the realm's open
client registration and needs no client ID.

| Product | Client ID | Checked | Date | Notes |
| --- | --- | --- | --- | --- |
| VS Code | `zato-test-vscode` | | | |
| Cursor | `zato-test-cursor` | | | |
| Claude Code | `zato-test-claude-code` | | | |
| Claude.ai and Claude Desktop | `zato-test-claude-ai` | | | |
| ChatGPT | registered by the product | | | |

## Against an Entra ID tenant

The tenant has the registrations the Entra ID section of `docs/ai/mcp/oauth.md` describes - the API registration
with its exposed scope and the token version set to 2, one public client per product with that product's redirect
URI, a confidential client for ChatGPT, and the groups claim on the API's tokens. Besides the steps above, each row
confirms that the `iss` and `aud` claims of the token the product obtained are the issuer and the audience the
walkthrough gives - `https://login.microsoftonline.com/<tenant-id>/v2.0` and the Application ID URI - which the
audit event's `auth` block shows under `issuer` and `audience`.

| Product | Client ID | Issuer and audience as documented | Checked | Date | Notes |
| --- | --- | --- | --- | --- | --- |
| VS Code | | | | | |
| Cursor | | | | | |
| Claude Code | | | | | |
| Claude.ai and Claude Desktop | | | | | |
| ChatGPT | | | | | |

## Coexistence

One server with two gateways - one with OAuth off, secured with an API key, and one with OAuth on. Cursor is
connected to the first with the key in `headers` and keeps listing and calling its tools while a sign-in to the
second one runs and completes from the same Cursor instance.

| Gateway with OAuth off keeps working | Checked | Date | Notes |
| --- | --- | --- | --- |
| Cursor with a configured header | | | |
