# AI chat widget for Zato dashboard

## Overview

This is a floating chat widget embedded in the Zato web-admin interface. It allows users to interact with AI services
directly from any page in the admin panel. The widget has a dark theme.

## Current status

The frontend and backend are complete. Chat streaming works with Anthropic, OpenAI, and Google providers.

## Architecture decisions

### API key storage

API keys are stored server-side in Redis, not in the browser's localStorage. This means:
- Keys never leave the server
- The browser only knows whether a key exists (boolean), not its value
- When chat is implemented, the browser will send messages to Django views which will fetch the key from Redis and make the API call

### Streaming approach

The existing `log_streaming.py` view demonstrates the SSE (Server-Sent Events) pattern using:
- `StreamingHttpResponse` with `content_type='text/event-stream'`
- A generator function that yields SSE-formatted messages
- Redis pub/sub for real-time data

This same pattern can be used for AI chat streaming responses.

## File locations

### JavaScript files

Location: `/zato-web-admin/src/zato/admin/static/js/ai-chat/`

Core modules:
- `ai-chat-core.js` - main entry point, initialization, state management, render orchestration
- `ai-chat-events.js` - event binding and delegation to other modules
- `ai-chat-click-handlers.js` - click event handler logic for all UI elements
- `ai-chat-streaming.js` - message sending, streaming, and live syntax highlighting
- `ai-chat-tab-actions.js` - tab operations (add, close, switch, focus)
- `ai-chat-window.js` - window state management (minimize, maximize)
- `ai-chat-state.js` - localStorage persistence for widget state
- `ai-chat-tab-state.js` - per-tab state manager (model, attachments, etc.)
- `ai-chat-render.js` - HTML building functions for header, tabs, body, messages, input area, footer
- `ai-chat-config.js` - provider configuration UI, model loading, API key management

Widget modules:
- `ai-chat-widget.js` - widget creation, position/dimension management, minimize/restore
- `ai-chat-drag.js` - widget drag, resize, tab reordering
- `ai-chat-zoom.js` - ctrl+wheel zoom using CSS transform scale
- `ai-chat-resize.js` - resize state management and calculations

UI modules:
- `ai-chat-tabs.js` - tab management (add, remove, rename, reorder)
- `ai-chat-input.js` - contenteditable input handling (shift+enter for newlines, backspace/delete line removal)
- `ai-chat-messages.js` - message adding and scrolling
- `ai-chat-context-menu.js` - right-click context menu for tab rename
- `ai-chat-settings.js` - settings menu, API key save/remove
- `ai-chat-options-menu.js` - options menu (add files, MCP, manage keys)

File handling modules:
- `ai-chat-attachments.js` - attachment icons, rendering, file handling, size limits
- `ai-chat-preview.js` - thin wrapper around ZatoPreview for attachment previews

Backend communication:
- `ai-chat-sse.js` - SSE connection management (connect, disconnect, event parsing)
- `ai-chat-api.js` - high-level API for streaming messages

Syntax highlighting:
- `ai-chat-highlight.js` - client-side syntax highlighting using highlight.js
- `hljs.min.js` - highlight.js library

Syntax highlighting CSS:
- Location: `/zato-web-admin/src/zato/admin/static/css/ai-chat/hljs-atom-one-dark.css`

Location: `/zato-web-admin/src/zato/admin/static/js/libs/`

Third-party libraries:
- `marked.min.js` - markdown parser
- `marked-emoji.min.js` - emoji shortcode extension for marked.js

Location: `/zato-web-admin/src/zato/admin/static/js/`

Reusable components:
- `zato-dropdown.js` - custom dropdown component (replaces native select elements)
- `zato-preview.js` - file preview popup component (draggable, supports PDF/Word/images/text, copy to clipboard)

### CSS files

Location: `/zato-web-admin/src/zato/admin/static/css/ai-chat/`

- `ai-chat-base.css` - widget container, body, panels, empty state
- `ai-chat-header.css` - header bar, tabs, tab buttons, dragging state, settings menu
- `ai-chat-messages.css` - message bubbles (user, assistant, system roles)
- `ai-chat-input.css` - input area, contenteditable div, send button, footer, options menu
- `ai-chat-resize.css` - corner resize handles
- `ai-chat-context-menu.css` - right-click context menu for tab rename
- `ai-chat-config.css` - provider configuration UI styling

Location: `/zato-web-admin/src/zato/admin/static/css/`

Reusable component styles:
- `zato-dropdown.css` - styles for custom dropdown component
- `zato-preview.css` - styles for file preview popup component

### Django views

Location: `/zato-web-admin/src/zato/admin/web/views/ai/`

- `common.py` - shared utilities:
  - `Providers` - tuple of valid provider names (single source of truth)
  - `get_redis_client()` - returns Redis client instance
  - `is_valid_provider()` - validates provider name
  - `get_api_key()` / `set_api_key()` / `delete_api_key()` - Redis key operations
  - `get_all_api_key_status()` - returns dict of provider -> bool

- `chat.py` - chat configuration endpoints:
  - `get_keys` - retrieves API key status for all providers
  - `save_key` - saves API key to Redis
  - `delete_key` - deletes API key from Redis
  - `get_models` - retrieves available AI models from models.py

- `stream.py` - SSE streaming endpoint:
  - `invoke` - POST endpoint that streams chat responses via SSE

- `highlight.py` - syntax highlighting endpoints:
  - `highlight_code` - POST endpoint that highlights code using Pygments
  - `get_pygments_css` - GET endpoint that returns Pygments CSS styles

### LLM clients

Location: `/zato-web-admin/src/zato/admin/web/views/ai/llm/`

- `base.py` - abstract base class for LLM clients
- `anthropic.py` - Anthropic Claude API client
- `openai.py` - OpenAI GPT API client
- `google.py` - Google Gemini API client
- `factory.py` - factory function to get client by provider name

### Model definitions

Location: `/zato-common/src/zato/common/ai/models.py`

Models are defined in an INI-style string embedded in Python:
```python
models_ini = """
[claude-opus-4-6]
provider = anthropic
name = Claude Opus 4.6
...
"""
```

Helper functions:
- `get_models_by_provider(provider)` - returns list of models for a provider
- `get_all_models()` - returns all models grouped by provider

### URL routes

Location: `/zato-web-admin/src/zato/admin/urls.py`

- `/zato/ai-chat/config/get-keys/` - GET API key status for all providers
- `/zato/ai-chat/config/save-key/` - POST to save API key
- `/zato/ai-chat/config/delete-key/` - POST to delete API key
- `/zato/ai-chat/config/get-models/` - GET available models for all providers
- `/zato/ai-chat/invoke/` - POST to stream chat response via SSE
- `/zato/ai-chat/highlight/` - POST to highlight code using Pygments
- `/zato/ai-chat/highlight/css/` - GET Pygments CSS styles

### Redis keys

- `zato.ai-chat.api-key.anthropic` - Anthropic API key
- `zato.ai-chat.api-key.openai` - OpenAI API key
- `zato.ai-chat.api-key.google` - Google Gemini API key

To delete all keys from Redis: `redis-cli DEL zato.ai-chat.api-key.anthropic zato.ai-chat.api-key.openai zato.ai-chat.api-key.google`

### HTML template

Location: `/zato-web-admin/src/zato/admin/templates/zato/index.html`

All JS and CSS files are included here in the correct dependency order.

## Features implemented

### Widget behavior

- Floating widget with fixed position
- Draggable by header (clamped to viewport, minimum top/left of 0)
- Resizable from all four corners (minimum 300x200)
- Minimizes to bottom-right corner (200px wide, header only)
- Restores to previous position and size
- Zone-based zoom via ctrl+wheel:
  - Hover over messages area to zoom chat bubbles
  - Hover over input field to zoom text input
  - Hover over input area (model selector, attachments) to zoom that section
  - Each zone has independent zoom level (0.7x to 1.5x)
  - Zone zoom levels persisted to localStorage
- Maximize button next to minimize button
- Double-click title bar to maximize/restore
- Maximized state persists across page refresh
- Widget resizes automatically when browser enters/exits fullscreen (F11)
- All state persisted to localStorage
- Header shows "AI chat" tag only when minimized
- Environment name tag displayed if Zato_Env_Name env variable is set

### Tabs

- Multiple chat tabs
- Add new tab with + button
- Close tab with X button (cannot close last tab)
- Rename tab via right-click context menu
- Drag-drop to reorder tabs (with 5px threshold to prevent accidental drags)
- Active tab highlighted with blue underline
- Tabs bar hidden when no API key is configured

### Input area

- Contenteditable div (not textarea)
- Placeholder text when empty
- Shift+Enter inserts line break
- Backspace/Delete removes one line at a time when only line breaks remain
- Enter sends message

### Input footer

- Located below the text input area
- Model selector dropdown on the left (custom ZatoDropdown component)
- Options button (+) and send button on the right
- Send button is prominent (36x36px, Zato blue background, white arrow-up icon)
- Options button opens menu with:
  - "Manage API keys" - opens key management screen
  - "Add files or photos" - opens file picker dialog
  - "Manage MCP servers" - opens MCP server management screen
- Model selector shows models grouped by provider with separators between providers
- Each tab stores its own selected model (persisted to localStorage)
- Footer has max-width of 600px and is centered on wide screens

### Attachments

- Pasting text longer than 8000 characters converts it to an attachment
- Attachments displayed as cards above the input area
- Each attachment shows: file icon, name, size, remove button
- Files selected via "Add files or images" also become attachments
- Attachments can be removed by clicking the X button
- Attachments persist across page reloads (saved to localStorage with tabs)
- Maximum file size: 10 MB
- Drag and drop files from file manager anywhere onto the widget to add as attachments
- Visual feedback: widget border turns blue dashed when dragging files over it

### File preview

- Click any attachment to open a preview popup
- Preview popup is draggable by header (except over the title text)
- Title text is selectable for copying the filename
- Multiple previews can be open simultaneously (stacked with offset)
- Clicking an already-open attachment brings its preview to front instead of opening duplicate
- Close with X button or Escape key (closes topmost preview)
- Supported preview types:
  - Images (PNG, JPEG, GIF, WebP, SVG, BMP) - displayed inline
  - PDFs - all pages rendered using pdf.js
  - Word documents (.docx) - rendered using mammoth.js
  - Text files (plain text, JSON, JavaScript, XML, etc.) - displayed in monospace
- Unsupported formats show "Preview not available" message
- Copy button copies content to clipboard:
  - Images: copies image data via canvas
  - PDFs: extracts and copies text from all pages
  - Word documents: copies rendered text
  - Text files: copies raw content

### Messages

- User messages aligned right with blue gradient background
- Assistant messages aligned left with dark background
- System messages centered with yellow-tinted background
- Messages sized to fit content (not full width)
- Auto-scroll to bottom on new message
- Markdown rendering using marked.js library
- Syntax highlighting for code blocks using highlight.js (client-side, atom-one-dark theme)
- Live syntax highlighting during streaming (highlights as code arrives)
- Emoji shortcodes supported (e.g., `:smile:` → 😀, `:fire:` → 🔥)
- ASCII emoticons supported (e.g., `:)` → 😊, `<3` → ❤️)
- Emoji tooltips show shortcode on hover
- Live emoji conversion in input field as you type
- Full timestamp display (YYYY-MM-DD HH:MM:SS format)
- Copy button on each message to copy content to clipboard
- Timestamp and copy button hidden during streaming, only cursor shown

### Token counters

- Display "Tok out: X" and "Tok in: X" next to model dropdown
- Tracks actual token counts from LLM API responses (not estimates)
- Tok out = input tokens sent to LLM (cumulative per tab)
- Tok in = output tokens received from LLM (cumulative per tab)
- Numbers humanized for readability (e.g., 1.2k, 15k, 1.5M)
- Token counts persisted per tab in localStorage

### Streaming

- Real-time streaming of LLM responses via SSE
- Markdown rendered live as chunks arrive
- Input field automatically focused after response completes
- Input field focused on page load, tab switch, and window focus

### Provider configuration

- Provider selection screen with Claude (Anthropic), GPT (OpenAI), and Gemini (Google)
- Provider names display as "<strong>Model</strong> · Company" format
- API key input screen with monospace font and autofocus
- Save button label is generic "Save API key" for all providers
- Configuration UI always centered in the widget regardless of widget size
- Configuration UI rendered once (not per-tab) to avoid duplicate input elements
- Back button navigation logic:
  - When user has an API key configured and clicks "Manage API keys": back button returns to chat
  - When user has no API key and is on provider selection: no back button shown
  - When user has no API key and is on key input: back button returns to provider selection
- Options menu accessed via + button in input footer (not header)
- Options menu contains:
  - "Manage API keys" - opens key management screen
  - "Add files or photos" - opens file picker dialog
  - "Manage MCP servers" - opens MCP server management screen
- Manage API keys screen:
  - Lists all providers with their logos
  - Shows "Add" button for providers without a key
  - Shows "Remove" button for providers with a configured key
  - Clicking "Add" navigates to API key input for that provider
  - Clicking "Remove" deletes the key and refreshes the list
  - If all keys are removed, returns to provider selection screen
- API keys stored in Redis via Django views
- Model dropdown shows all models from all providers
- Models without configured API keys appear dimmed (grayed out) but visible
- Dimmed models cannot be selected until their provider's API key is added
- When a previously selected model becomes unavailable, automatically selects first available model

## Logging

### Backend logging

The Anthropic client logs all requests and responses at INFO level:
- `Anthropic request: model=X messages=[...]` - full request with all messages
- `Anthropic event: X data=Y` - each SSE event from the API
- `Anthropic input_tokens: X` - input token count from API
- `Anthropic output_tokens: X` - output token count from API
- `Anthropic complete: input_tokens=X output_tokens=Y` - final token counts

### Frontend logging

The frontend logs token data to browser console:
- `AIChatSSE done: input_tokens=X output_tokens=Y data=...` - token data received
- `onComplete: inputTokens=X outputTokens=Y` - tokens passed to handler
- `after addTokensOut: X` - cumulative output tokens
- `after addTokensIn: X` - cumulative input tokens

## localStorage keys

- `zato.ai-chat.tabs` - array of tab objects with id, title, messages, model, tokensIn, tokensOut
- `zato.ai-chat.active-tab` - id of active tab
- `zato.ai-chat.position` - {left, top} of widget
- `zato.ai-chat.dimensions` - {width, height} of widget
- `zato.ai-chat.minimized` - "true" or "false"
- `zato.ai-chat.maximized` - "true" or "false"
- `zato.ai-chat.pre-minimize-position` - {left, top, width, height} before minimizing
- `zato.ai-chat.pre-maximize-state` - {left, top, width, height} before maximizing
- `zato.ai-chat.zoom` - zoom scale (legacy, no longer used for widget zoom)
- `zato.ai-chat.zone-zoom` - {messages, inputArea, input} zone zoom scales

## Debug flags

- `AIChatInput.debugKeystrokes` - set to `true` to enable detailed keystroke logging with cursor position info (default: `false`)

## Configuration

- `AIChatInput.pasteToAttachmentThreshold` - character count threshold for converting pasted text to attachment (default: `8000`)

## Code style notes

- No ES6+ features (no arrow functions, no const/let, no template literals)
- All modules use IIFE pattern and attach to window object
- Debug logging via console.debug with module prefix
- No global variables except the module objects on window
- No global variable assignments, no window object assignments except module exports
- No icons in menus unless explicitly requested
- No tooltips on buttons unless explicitly requested
- No text shadows anywhere
- No fade effects or transitions on tab switching
- No hover jump effects on provider cards
- Use Zato CSS variables for button colors (--zato-seablue, --zato-seablue-light1, etc.)
- Provider configuration UI must be vertically centered automatically (flexbox, no hardcoded positions)
- Back button positioned absolutely at top-left of messages container
- API key input uses monospace font
- When adding new providers:
  1. Add provider object to `AIChatConfig.providers` in ai-chat-config.js
  2. Add provider to `providerOrder` array in `getModelsForConfiguredProviders`
  3. Add provider to `hasAnyKey()` check
  4. Add models to models.py with provider field
  5. Add provider to `get_all_models()` result dict in models.py
  6. Add provider to Django views (get_keys, save_key, delete_key)

## UI styling rules

- Dark theme throughout
- Input fields: dark background (#252525), no white shadows, blue-only focus shadow
- Buttons: use Zato blue variables, no gradients, no text shadows
- Provider names format: "<strong>ModelName</strong> · CompanyName"
- Send button: prominent size (36x36px), Zato blue background, white arrow-up icon
- Options button: smaller (28px), transparent background, + icon
- Model selector: custom dropdown (ZatoDropdown), not native select
- Model dropdown shows separators between different providers
- Empty state ("Start a conversation") hides scrollbar
- Back button behavior:
  - When user has an API key configured and clicks "Manage API keys": back button returns to chat
  - When user has no API key and is on provider selection: no back button shown
  - When user has no API key and is on key input: back button returns to provider selection
  - When on manage keys screen: back button returns to chat

## Naming conventions

- Use sentence case for labels, not title case (e.g., "Attach file" not "Attach File")
- Menu items use sentence case (e.g., "Manage API keys", "Add files or photos")

## MCP (Model Context Protocol) integration

### Overview

The widget supports connecting to MCP servers to extend LLM capabilities with external tools.

### MCP JavaScript module

Location: `/zato-web-admin/src/zato/admin/static/js/ai-chat/ai-chat-mcp.js`

- `AIChatMCP.servers` - array of configured MCP servers
- `AIChatMCP.loadServers(callback)` - loads servers from backend
- `AIChatMCP.addServer(endpoint, callback)` - adds a new server (name extracted from URL)
- `AIChatMCP.removeServer(serverId, callback)` - removes a server
- `AIChatMCP.updateServer(serverId, updates, callback)` - updates server settings
- `AIChatMCP.getTools(callback)` - retrieves tools from all enabled servers
- `AIChatMCP.buildManageServersHtml()` - builds the server management UI
- `AIChatMCP.buildServerDetailHtml(server, tools, loading)` - builds server detail view with tools list
- `AIChatMCP.buildAddServerHtml()` - builds the add server form
- `AIChatMCP.buildEditServerHtml(server)` - builds the edit server form

### MCP CSS

Location: `/zato-web-admin/src/zato/admin/static/css/ai-chat/ai-chat-mcp.css`

### MCP backend

Location: `/zato-web-admin/src/zato/admin/web/views/ai/mcp/`

- `base.py` - MCPClient class implementing JSON-RPC 2.0 over HTTP with SSE
- `registry.py` - MCPRegistry class for managing servers in Redis
- `views.py` - Django views for MCP server CRUD and tool invocation

### MCP URL routes

- `/zato/ai-chat/mcp/servers/` - GET list of servers
- `/zato/ai-chat/mcp/add/` - POST to add a server
- `/zato/ai-chat/mcp/remove/` - POST to remove a server
- `/zato/ai-chat/mcp/update/` - POST to update a server
- `/zato/ai-chat/mcp/tools/` - GET tools from all enabled servers
- `/zato/ai-chat/mcp/invoke/` - POST to invoke a tool

### MCP Redis key

- `zato.ai-chat.mcp-servers` - JSON array of MCP server configurations

### MCP UI features

- "Manage MCP servers" option in the options menu
- Server list with toggle switch (enable/disable), edit and remove buttons
- Empty state shows "No MCP servers configured" with centered "Add server" button
- "Add server" button in header row (right side of title) when servers exist
- Click server name to view list of available tools
- Edit server endpoint via edit button
- Remove confirmation: click "Remove" → shows "Really?" for 2.2 seconds → click again to confirm
- Add/edit forms auto-focus the endpoint input field
- Save button shows spinner with "Connecting..." / "Saving..." while processing
- Error popup displays full error message (draggable, resizable, dark theme)
- URL validation: rejects invalid URLs and shows error message
- Tool descriptions displayed in lighter color (#c0c0c0) for readability

### MCP protocol

- Generic MCP client implementing JSON-RPC 2.0 over HTTP with SSE
- Initialize handshake with `initialize` method to get server info and capabilities
- Session ID captured from `mcp-session-id` response header and sent with subsequent requests
- Tools fetched via `tools/list` method
- Tool invocation via `tools/call` method
- User-Agent header: `Zato-MCP-Client`
- Accept header: `application/json, text/event-stream`
- Full tracebacks logged on errors

## Reusable confirm button component

Location: `/zato-web-admin/src/zato/admin/static/js/ai-chat/ai-chat-confirm.js`

`ZatoConfirmButton` - reusable component for Edit/Remove buttons with confirmation flow:
- `ZatoConfirmButton.buildEditHtml(itemId, extraClass)` - builds edit button HTML
- `ZatoConfirmButton.buildRemoveHtml(itemId, extraClass)` - builds remove button HTML
- `ZatoConfirmButton.handleClick(button, onConfirm)` - handles click with confirmation
- `ZatoConfirmButton.reset(button)` - resets button to initial state

Confirmation flow:
1. First click changes "Remove" to "Really?" with lighter background
2. If no second click within 2.2 seconds, reverts to "Remove"
3. Second click within timeout triggers the removal action
4. Timer ID stored on button element (data-timer-id) for independent operation

CSS: `/zato-web-admin/src/zato/admin/static/css/ai-chat/ai-chat-confirm.css`

## CSS variables

Location: `/zato-web-admin/src/zato/admin/static/css/ai-chat/ai-chat-variables.css`

Common colors defined as CSS variables:
- `--ai-chat-bg-dark`, `--ai-chat-bg-medium`, `--ai-chat-bg-light` - background colors
- `--ai-chat-text-primary`, `--ai-chat-text-secondary`, `--ai-chat-text-muted`, `--ai-chat-text-dim` - text colors
- `--ai-chat-border-subtle`, `--ai-chat-border-light` - border colors
- `--ai-chat-link-color`, `--ai-chat-link-hover` - link colors
- `--ai-chat-user-bg`, `--ai-chat-user-border`, `--ai-chat-user-accent` - user message colors
- `--ai-chat-assistant-bg`, `--ai-chat-assistant-border`, `--ai-chat-assistant-accent` - assistant message colors
- `--ai-chat-env-tag-bg`, `--ai-chat-env-tag-border` - environment tag colors
- `--ai-chat-error-bg`, `--ai-chat-error-color`, `--ai-chat-error-hover` - error/remove button colors
- `--ai-chat-toggle-on`, `--ai-chat-toggle-off` - toggle switch colors

## Config mode persistence

The current config screen (manage-mcp, manage-keys, add-mcp, etc.) is persisted to localStorage:
- Key: `zato.ai-chat.config-mode`
- On page refresh, user returns to the same config screen they were on
- Cleared when returning to chat or provider selection

## Keyboard shortcuts

- Backspace on config pages (when not in input field) triggers back button
- Enter in MCP endpoint input submits the form
- Escape closes error popup

## Reusable assets

### Spinner

Location: `/zato-web-admin/src/zato/admin/static/img/spinner.svg`

SVG spinner with `currentColor` fill for easy color customization via CSS.

Usage:
```html
<img src="/static/img/spinner.svg" class="ai-chat-spinner-icon" alt="">
```

CSS classes:
- `.ai-chat-spinner-icon` - 16x16, white (via CSS filter), for inline use in buttons
- `.ai-chat-spinner-icon.ai-chat-spinner-large` - 24x24 variant for loading states

### Error popup

Location: `/zato-web-admin/src/zato/admin/static/js/ai-chat/ai-chat-error.js`

`AIChatError.show(message)` - displays a draggable, resizable error popup with:
- Dark theme matching the widget
- Close button styled like header buttons
- Textarea for error message (readonly, monospace)
- Escape key to close
- Handles both string and object error messages
