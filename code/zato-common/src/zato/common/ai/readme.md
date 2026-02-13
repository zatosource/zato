# AI chat widget for Zato dashboard

## Overview

This is a floating chat widget embedded in the Zato web-admin interface. It allows users to interact with AI services
directly from any page in the admin panel. The widget has a dark theme.

## Current status

The frontend is complete including provider configuration UI. The backend integration is not yet implemented.

## File locations

### JavaScript files

Location: `/zato-web-admin/src/zato/admin/static/js/ai-chat/`

- `ai-chat-state.js` - localStorage persistence for tabs, position, dimensions, zoom, minimized state
- `ai-chat-render.js` - HTML building functions for header, tabs, body, messages, input area
- `ai-chat-tabs.js` - tab management (add, remove, rename, reorder, drag-drop)
- `ai-chat-input.js` - contenteditable input handling (shift+enter for newlines, backspace/delete line removal)
- `ai-chat-resize.js` - widget drag and corner resize
- `ai-chat-zoom.js` - ctrl+wheel zoom using CSS transform scale
- `ai-chat-messages.js` - message adding and scrolling
- `ai-chat-api.js` - backend communication (stub, not implemented)
- `ai-chat-config.js` - provider configuration UI (provider selection, API key input, settings menu)
- `ai-chat-core.js` - main entry point, initialization, event binding, state coordination

### CSS files

Location: `/zato-web-admin/src/zato/admin/static/css/ai-chat/`

- `ai-chat-base.css` - widget container, body, panels, empty state
- `ai-chat-header.css` - header bar, tabs, tab buttons, dragging state, settings menu
- `ai-chat-messages.css` - message bubbles (user, assistant, system roles)
- `ai-chat-input.css` - input area, contenteditable div, send button
- `ai-chat-resize.css` - corner resize handles
- `ai-chat-context-menu.css` - right-click context menu for tab rename
- `ai-chat-config.css` - provider configuration UI styling

### Django views

Location: `/zato-web-admin/src/zato/admin/web/views/ai_chat.py`

- `get_keys` - retrieves API key status for all providers from Redis
- `save_key` - saves API key to Redis

### URL routes

Location: `/zato-web-admin/src/zato/admin/urls.py`

- `/zato/ai-chat/config/get-keys/` - GET API key status for all providers
- `/zato/ai-chat/config/save-key/` - POST to save API key

### Redis keys

- `zato.ai-chat.api-key.anthropic` - Anthropic API key
- `zato.ai-chat.api-key.openai` - OpenAI API key

To delete keys from Redis: `redis-cli DEL zato.ai-chat.api-key.anthropic zato.ai-chat.api-key.openai`

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
- Zoom via ctrl+wheel (0.5x to 2.0x scale, resets to 1.0 when minimized)
- All state persisted to localStorage
- Settings menu in header (shows on hover, no click required)
- Settings menu button (hamburger icon) hidden when widget is minimized

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
- Shift+Enter inserts line break and expands to multiline mode
- Backspace/Delete removes one line at a time when only line breaks remain
- Enter sends message
- Send button with arrow icon

### Messages

- User messages aligned right with blue gradient background
- Assistant messages aligned left with dark background
- System messages centered with yellow-tinted background
- Messages sized to fit content (not full width)
- Auto-scroll to bottom on new message

### Provider configuration

- Provider selection screen with Claude (Anthropic) and GPT (OpenAI)
- Provider names display as "<strong>Model</strong> · Company" format
- API key input screen with monospace font and autofocus
- Configuration UI always centered in the widget regardless of widget size
- Back button navigation logic:
  - When user has an API key configured and clicks "Change provider" or "Change API key": back button returns to chat
  - When user has no API key and is on provider selection: no back button shown
  - When user has no API key and is on key input: back button returns to provider selection (no back button on providers)
- Settings menu options depend on whether API key is configured:
  - With key: "Change provider" and "Change API key"
  - Without key: "Configure provider" only
- API keys stored in Redis via Django views
- Button labels use lookup map for extensibility (e.g., "Use Claude", "Use GPT")

## Next steps - backend integration

### Service to implement

Service name: `zato.server.service.internal.ai.chat.invoke`

Request format (JSON):
```json
{
    "chat_id": "string",
    "message": "string"
}
```

Response format (JSON):
```json
{
    "response": "string"
}
```

### Frontend changes needed

The file `ai-chat-api.js` contains stub functions that need to be implemented:

1. `sendMessage(message, tabId, onSuccess, onError)` - send message to backend, call onSuccess with response
2. `streamMessage(message, tabId, onChunk, onComplete, onError)` - for streaming responses (optional)

The `ai-chat-core.js` `sendMessage` method currently only adds the user message to the tab and re-renders. It needs to:

1. Call `AIChatAPI.sendMessage()` with the message
2. Show a loading indicator while waiting
3. On success, add the assistant response to the tab
4. On error, show an error message

### API endpoint

A Django view is needed in zato-web-admin to proxy requests to the Zato service. The frontend will POST to this endpoint.

Suggested URL: `/zato/ai-chat/invoke/`

The view should:
1. Accept POST with JSON body containing `chat_id` and `message`
2. Invoke the `zato.server.service.internal.ai.chat.invoke` service
3. Return the response JSON

### Authentication

Use existing Zato admin session authentication. The Django view will have access to the authenticated user.

## localStorage keys

- `zato.ai-chat.tabs` - array of tab objects with id, title, messages
- `zato.ai-chat.active-tab` - id of active tab
- `zato.ai-chat.position` - {left, top} of widget
- `zato.ai-chat.dimensions` - {width, height} of widget
- `zato.ai-chat.minimized` - "true" or "false"
- `zato.ai-chat.pre-minimize-position` - {left, top, width, height} before minimizing
- `zato.ai-chat.zoom` - zoom scale (0.5 to 2.0)

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
- Button labels stored in lookup map for extensibility (not if/else)
- When adding new providers, add entry to buttonLabels map in ai-chat-config.js

## UI styling rules

- Dark theme throughout
- Input fields: dark background (#252525), no white shadows, blue-only focus shadow
- Buttons: use Zato blue variables, no gradients, no text shadows
- Provider names format: "<strong>ModelName</strong> · CompanyName"
- Settings menu appears on hover (no click required)
- Back button behavior:
  - When user has an API key configured and clicks "Change provider" or "Change API key": back button returns to chat
  - When user has no API key and is on provider selection: no back button shown
  - When user has no API key and is on key input: back button returns to provider selection
