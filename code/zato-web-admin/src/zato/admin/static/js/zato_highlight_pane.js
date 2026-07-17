
// ////////////////////////////////////////////////////////////////////////
//
// Reusable syntax-highlighted editor pane for the Zato Dashboard.
//
// Wraps Ace editor with Monokai theme and an optional configurable button footer.
// Has no dependency on dashboard-kit - only on zato_ui_helpers.js and Ace.
//
// Prerequisites (load before this script):
//   - jQuery
//   - ace.js (from /static/ace-builds/src/ace.js)
//   - zato_ui_helpers.js
//   - zato_highlight_pane.css
//
// Usage - syntax-only, no buttons:
//
//   $.fn.zato.highlight_pane.init({
//       container: '#my-container',
//       text: '{"hello": "world"}',
//       editable: false
//   });
//
// Usage - editable with copy and save buttons:
//
//   var pane = $.fn.zato.highlight_pane.init({
//       container: '#my-container',
//       text: myData,
//       editable: true,
//       buttons: [
//           $.fn.zato.highlight_pane.buttons.copy(),
//           $.fn.zato.highlight_pane.buttons.save({
//               poll_url: '/zato/dashboard/detail-poll/',
//               save_action: 'update-something',
//               hidden_fields: {my_id: '123'},
//               on_success: function(response, pane) { ... },
//               on_error: function(errorMessage, pane) { ... }
//           })
//       ]
//   });
//
// Usage - custom buttons:
//
//   $.fn.zato.highlight_pane.init({
//       container: '#viewer',
//       text: logOutput,
//       editable: false,
//       buttons: [
//           {id: 'my-button', label: 'Download', on_click: function(buttonElement, pane) {
//               downloadAsFile(pane.getValue());
//           }}
//       ]
//   });
//
// Config options for init:
//
//   container        - css selector for the mount point (required)
//   text             - initial text content (required)
//   editable         - boolean, default true, whether the editor allows editing
//   ace_options      - optional object with theme and fontSize overrides
//   ace_mode         - optional ace mode string (e.g. 'ace/mode/json'), defaults to 'ace/mode/text'
//   buttons          - optional array of {id, label, on_click} button definitions,
//                      if omitted or empty, no footer is rendered
//
// Returned pane instance:
//
//   pane.getValue()   - returns the current editor text
//   pane.setValue(text, mode) - sets editor text and optionally sets ace mode
//   pane.getEditor()  - returns the raw Ace editor instance
//   pane.destroy()    - tears down the Ace editor and clears the container
//
// Built-in button factories:
//
//   $.fn.zato.highlight_pane.buttons.copy()
//     Creates a Copy button that copies selected text (or all text if nothing
//     is selected) to the clipboard with a tooltip confirmation.
//
//   $.fn.zato.highlight_pane.buttons.save(config)
//     Creates a Save button that posts editor content to config.poll_url.
//     Config: poll_url, save_action, hidden_fields (object), on_success, on_error.
//
// ////////////////////////////////////////////////////////////////////////

(function($) {

    $.namespace('zato.highlight_pane');

    var uiHelpers = $.fn.zato.ui_helpers;

    var _labels = {
        copy: 'Copy',
        save: 'Save',
        saved: 'OK, saved',
        saveFailed: 'Save failed'
    };

// ////////////////////////////////////////////////////////////////////////

    var _mime_ace_modes = {
        'application/json': 'ace/mode/json',
        'text/json': 'ace/mode/json',
        'application/geo+json': 'ace/mode/json',
        'application/ld+json': 'ace/mode/json',
        'application/vnd.api+json': 'ace/mode/json',
        'application/json5': 'ace/mode/json5',
        'text/xml': 'ace/mode/xml',
        'application/xml': 'ace/mode/xml',
        'application/soap+xml': 'ace/mode/xml',
        'application/xhtml+xml': 'ace/mode/html',
        'application/rss+xml': 'ace/mode/xml',
        'application/atom+xml': 'ace/mode/xml',
        'image/svg+xml': 'ace/mode/svg',
        'text/html': 'ace/mode/html',
        'text/yaml': 'ace/mode/yaml',
        'text/x-yaml': 'ace/mode/yaml',
        'application/x-yaml': 'ace/mode/yaml',
        'application/yaml': 'ace/mode/yaml',
        'text/csv': 'ace/mode/text',
        'text/plain': 'ace/mode/text',
        'application/octet-stream': 'ace/mode/text',
    };

    $.fn.zato.highlight_pane.mime_to_ace_mode = function(mimeType) {
        var out = _mime_ace_modes[mimeType];
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.highlight_pane.detect_ace_mode = _detect_ace_mode;

    function _detect_ace_mode(text) {
        var trimmed = text.trim();
        var out;

        // Check for HL7 v2 messages ..
        if (trimmed.indexOf('MSH|') === 0) {
            out = 'ace/mode/hl7';
        }

        // .. check for Python traceback markers ..
        else if (trimmed.indexOf('Traceback') !== -1) {
            out = 'ace/mode/python_traceback';
        }
        else if (trimmed.indexOf('File "') !== -1) {
            out = 'ace/mode/python_traceback';
        }
        else if (trimmed.indexOf('\u00b7\u00b7\u00b7 Error \u00b7\u00b7\u00b7') !== -1) {
            out = 'ace/mode/python_traceback';
        }

        // .. otherwise use plain text.
        else {
            out = 'ace/mode/text';
        }

        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    function _bindButtonClick(buttonElement, clickHandler, pane) {
        function handleClick() {
            clickHandler(buttonElement, pane);
        }
        buttonElement.addEventListener('click', handleClick);
    }

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.highlight_pane.init = function(config) {

        var $container = $(config.container);

        // Determine if the editor should be editable ..
        var editable = true;

        if (config.editable === false) {
            editable = false;
        }

        // .. build the editor element ..
        var editorElement = document.createElement('div');
        editorElement.className = 'zato-highlight-pane-editor';
        $container.append(editorElement);

        // .. the observer resizing the editor along with its container, if one is requested below -
        // .. it is kept here so destroy can disconnect it before the editor goes away ..
        var resizeObserver = null;

        // .. set up the Ace editor ..
        var editor = ace.edit(editorElement);
        editor.setTheme('ace/theme/monokai');
        editor.setShowPrintMargin(false);
        editor.setFontSize(12);
        editor.setOptions({
            fontFamily: 'Menlo, Consolas, Monaco, monospace',
            firstLineNumber: 1
        });
        editor.renderer.setScrollMargin(7, 0, 0, 0);
        editor.setReadOnly(!editable);

        // .. apply any custom Ace options ..
        if (config.ace_options) {

            if (config.ace_options.theme) {
                editor.setTheme(config.ace_options.theme);
            }

            if (config.ace_options.fontSize) {
                editor.setFontSize(config.ace_options.fontSize);
            }

            if (config.ace_options.maxLines) {
                editor.setOption('maxLines', config.ace_options.maxLines);
                editorElement.style.minHeight = 'auto';
                editorElement.style.height = 'auto';
            }

            if (config.ace_options.minLines) {
                editor.setOption('minLines', config.ace_options.minLines);
            }

            if (config.ace_options.alwaysShowScrollbars) {
                editor.renderer.$vScrollBarAlwaysVisible = true;
                editor.renderer.$hScrollBarAlwaysVisible = true;
            }

            if (config.ace_options.resizable) {
                editorElement.style.resize = 'vertical';
                editorElement.style.overflow = 'hidden';
                resizeObserver = new ResizeObserver(function() {
                    editor.resize();
                });
                resizeObserver.observe(editorElement);
            }
        }

        // .. determine the mode from config or by detection ..
        var mode;
        if (config.ace_mode) {
            mode = config.ace_mode;
        }
        else {
            mode = _detect_ace_mode(config.text);
        }

        // .. and set the initial text and mode.
        editor.setValue(config.text, -1);
        editor.session.setMode(mode);

        // .. build the pane instance that callers interact with ..
        var pane = {

            getValue: function() {
                return editor.getValue();
            },

            setValue: function(text, mode) {
                editor.setValue(text, -1);
                if (mode) {
                    editor.session.setMode(mode);
                }
            },

            getEditor: function() {
                return editor;
            },

            destroy: function() {

                // Stop observing first - a resize callback pending at this point
                // must never run against an editor that no longer exists.
                if (resizeObserver) {
                    resizeObserver.disconnect();
                    resizeObserver = null;
                }

                editor.destroy();
                $container.empty();
            }
        };

        // .. render the footer buttons if any were configured ..
        if (config.buttons) {
            if (config.buttons.length > 0) {

                var footer = document.createElement('div');
                footer.className = 'zato-highlight-pane-footer';

                for (var buttonIndex = 0; buttonIndex < config.buttons.length; buttonIndex++) {
                    var buttonConfig = config.buttons[buttonIndex];
                    var buttonElement = document.createElement('button');
                    buttonElement.className = 'zato-action-button';
                    buttonElement.setAttribute('type', 'button');
                    buttonElement.textContent = buttonConfig.label;

                    if (buttonConfig.id) {
                        buttonElement.id = buttonConfig.id;
                    }

                    _bindButtonClick(buttonElement, buttonConfig.on_click, pane);

                    footer.appendChild(buttonElement);
                }

                $container.append(footer);
            }
        }

        // .. and return the pane instance.
        return pane;
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.highlight_pane.buttons = {};

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.highlight_pane.buttons.copy = function() {
        return {
            id: 'zato-highlight-pane-copy',
            label: _labels.copy,
            on_click: function(buttonElement, pane) {
                var selected = pane.getEditor().getSelectedText();
                var text = selected;

                if (!selected) {
                    text = pane.getValue();
                }

                uiHelpers.copy_to_clipboard(buttonElement, text);
            }
        };
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.highlight_pane.buttons.save = function(config) {
        return {
            id: 'zato-highlight-pane-save',
            label: _labels.save,
            on_click: function(buttonElement, pane) {

                // Collect the payload from the editor and hidden fields ..
                var editorValue = pane.getValue();

                var payload = {
                    action: config.save_action,
                    data: editorValue
                };

                if (config.hidden_fields) {
                    for (var fieldName in config.hidden_fields) {
                        payload[fieldName] = config.hidden_fields[fieldName];
                    }
                }

                // .. and POST it.
                $.ajax({
                    type: 'POST',
                    url: config.poll_url,
                    headers: {'X-CSRFToken': $.cookie('csrftoken')},
                    data: JSON.stringify(payload),
                    contentType: 'application/json',
                    success: function(response) {
                        uiHelpers.flash_tooltip(buttonElement, _labels.saved);

                        if (config.on_success) {
                            config.on_success(response, pane);
                        }
                    },
                    error: function(xhr) {
                        var errorMessage = _labels.saveFailed;

                        if (xhr.responseJSON) {
                            if (xhr.responseJSON.error) {
                                errorMessage = xhr.responseJSON.error;
                            }
                        }

                        uiHelpers.flash_tooltip(buttonElement, errorMessage);

                        if (config.on_error) {
                            config.on_error(errorMessage, pane);
                        }
                    }
                });
            }
        };
    };

// ////////////////////////////////////////////////////////////////////////
// Overlay mode - mounts the highlight pane inside a draggable modal shell.
//
// Besides the init options, open_overlay accepts:
//
//   title        - the overlay heading (required)
//   title_detail - optional selectable text after the heading, e.g. a CID
//   tabs         - optional array of {label, text, ace_mode} objects - when given,
//                  a tab bar precedes the editor and clicking a tab swaps
//                  the editor content for that tab's, the first tab being
//                  the initial one
// ////////////////////////////////////////////////////////////////////////

    var _$overlay = null;
    var _currentPane = null;

    function _build_overlay_dom() {
        var html = '' +
            '<div class="zato-highlight-pane-overlay hidden" id="zato-highlight-pane-overlay">' +
                '<div class="zato-highlight-pane-overlay-backdrop"></div>' +
                '<div class="zato-highlight-pane-overlay-content">' +
                    '<div class="zato-highlight-pane-overlay-header">' +
                        '<h2 class="zato-highlight-pane-overlay-title"></h2>' +
                        '<button class="zato-highlight-pane-overlay-close-btn" type="button">\u00d7</button>' +
                    '</div>' +
                    '<div class="zato-highlight-pane-overlay-body"></div>' +
                '</div>' +
            '</div>';

        _$overlay = $(html);
        $('body').append(_$overlay);

        _$overlay.find('.zato-highlight-pane-overlay-backdrop').on('click', function() {
            $.fn.zato.highlight_pane.close_overlay();
        });

        _$overlay.find('.zato-highlight-pane-overlay-close-btn').on('click', function() {
            $.fn.zato.highlight_pane.close_overlay();
        });

        $(document).on('keydown.zato_highlight_overlay', function(e) {
            if (e.key === 'Escape') {
                $.fn.zato.highlight_pane.close_overlay();
            }
        });

        // Double-clicking the selectable part of the title selects all of it,
        // so it can be copied manually even though the header itself is a drag handle.
        _$overlay.on('dblclick', '.zato-highlight-pane-overlay-title-detail', function() {
            var range = document.createRange();
            range.selectNodeContents(this);

            var selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
        });

        _make_overlay_draggable(_$overlay);
    }

    function _make_overlay_draggable($overlay) {
        var isDragging = false;
        var offsetX = 0;
        var offsetY = 0;
        var $content = $overlay.find('.zato-highlight-pane-overlay-content');
        var $header = $overlay.find('.zato-highlight-pane-overlay-header');

        $header.on('mousedown.zato_highlight_overlay', function(e) {
            if ($(e.target).is('button, input, a')) return;
            if ($(e.target).closest('.zato-highlight-pane-overlay-title-detail').length) return;
            isDragging = true;
            var rect = $content[0].getBoundingClientRect();
            offsetX = e.clientX - rect.left;
            offsetY = e.clientY - rect.top;
            $content.css({position: 'fixed', margin: '0', left: rect.left + 'px', top: rect.top + 'px', transform: 'none'});
            e.preventDefault();
        });

        $(document).on('mousemove.zato_highlight_overlay', function(e) {
            if (!isDragging) return;
            $content.css({left: (e.clientX - offsetX) + 'px', top: (e.clientY - offsetY) + 'px'});
        });

        $(document).on('mouseup.zato_highlight_overlay', function() {
            isDragging = false;
        });
    }

    $.fn.zato.highlight_pane.open_overlay = function(config) {
        if (!_$overlay) {
            _build_overlay_dom();
        }

        // Tear down any previous pane instance ..
        if (_currentPane) {
            _currentPane.destroy();
            _currentPane = null;
        }

        // .. set the title, with an optional selectable detail part after the main text ..
        var $title = _$overlay.find('.zato-highlight-pane-overlay-title');
        $title.text(config.title);

        if (config.title_detail) {
            var detailElement = document.createElement('span');
            detailElement.className = 'zato-highlight-pane-overlay-title-detail';
            detailElement.textContent = config.title_detail;

            $title.append(' ');
            $title.append(detailElement);
        }

        // .. reset position ..
        var $content = _$overlay.find('.zato-highlight-pane-overlay-content');
        $content.css({position: '', margin: '', left: '', top: '', transform: ''});

        // .. clear the body ..
        var $body = _$overlay.find('.zato-highlight-pane-overlay-body');
        $body.empty();

        // .. with tabs, a tab bar precedes the editor and the first tab provides the initial content ..
        var initialText = config.text;
        var initialMode = config.ace_mode;

        if (config.tabs) {

            var tabBar = document.createElement('div');
            tabBar.className = 'zato-highlight-pane-overlay-tabs';

            for (var tabIdx = 0; tabIdx < config.tabs.length; tabIdx++) {
                var tabConfig = config.tabs[tabIdx];
                var tabButton = document.createElement('button');
                tabButton.className = 'zato-highlight-pane-overlay-tab';
                tabButton.setAttribute('type', 'button');
                tabButton.setAttribute('data-tab-index', tabIdx);
                tabButton.textContent = tabConfig.label;
                tabBar.appendChild(tabButton);
            }

            $body.append(tabBar);

            initialText = config.tabs[0].text;
            initialMode = config.tabs[0].ace_mode;
        }

        // .. mount the highlight pane ..
        _currentPane = $.fn.zato.highlight_pane.init({
            container: $body,
            text: initialText,
            editable: config.editable,
            buttons: config.buttons,
            ace_options: config.ace_options,
            ace_mode: initialMode
        });

        // .. clicking a tab swaps the editor content for that tab's ..
        if (config.tabs) {
            var $tabs = $body.find('.zato-highlight-pane-overlay-tab');
            $tabs.first().addClass('zato-highlight-pane-overlay-tab-active');

            $tabs.on('click', function() {
                var tabIndex = parseInt($(this).attr('data-tab-index'), 10);
                var tab = config.tabs[tabIndex];

                _currentPane.setValue(tab.text, tab.ace_mode);

                $tabs.removeClass('zato-highlight-pane-overlay-tab-active');
                $(this).addClass('zato-highlight-pane-overlay-tab-active');
            });
        }

        // .. and show the overlay.
        _$overlay.removeClass('hidden');
    };

    $.fn.zato.highlight_pane.close_overlay = function() {
        if (_$overlay) {
            _$overlay.addClass('hidden');
        }
        if (_currentPane) {
            _currentPane.destroy();
            _currentPane = null;
        }
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
