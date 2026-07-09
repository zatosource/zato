
// Mapper kit - the overlay editor.
// One editor component used everywhere text is edited with highlighting:
// a transparent native textarea stacked on a pre showing the same text
// highlighted, kept in sync on input and scroll. The user types into a
// real textarea, so keyboards, selection and native undo work everywhere.
// A keyboard-driven autocomplete dropdown is fed by the schema paths and
// function names the caller supplies, and a gutter shows error markers
// from the caller's validation records.

(function($) {

    var config = zato.mapper.config;

    zato.mapper.overlayEditor = {};

// ////////////////////////////////////////////////////////////////////////

    var highlighters = {
        json: function(text) { return zato.mapper.highlight.json(text); },
        expression: function(text) { return zato.mapper.highlight.expression(text); }
    };

// ////////////////////////////////////////////////////////////////////////

    // Creates one editor.
    // editorConfig:
    //   container:     the element the editor renders into
    //   language:      'json' or 'expression'
    //   value:         initial text
    //   onChange:      called with the new text after every edit
    //   completions:   optional, a function returning [{label, doc, category}]
    //                  to offer - items sharing a non-empty category render
    //                  under one header
    //   ariaLabel:     accessible name of the textarea
    // Returns {getValue, setValue, setErrors, focus, element}.
    zato.mapper.overlayEditor.create = function(editorConfig) {

        var highlighter = highlighters[editorConfig.language];

        var wrapper = document.createElement('div');
        wrapper.className = 'mapper-editor';

        var gutter = document.createElement('div');
        gutter.className = 'mapper-editor-gutter';
        wrapper.appendChild(gutter);

        var stack = document.createElement('div');
        stack.className = 'mapper-editor-stack';

        var display = document.createElement('pre');
        display.className = 'mapper-editor-display';
        stack.appendChild(display);

        var input = document.createElement('textarea');
        input.className = 'mapper-editor-input';
        input.spellcheck = false;
        input.setAttribute('aria-label', editorConfig.ariaLabel);
        stack.appendChild(input);

        wrapper.appendChild(stack);

        var dropdown = document.createElement('ul');
        dropdown.className = 'mapper-editor-completions';
        dropdown.hidden = true;
        wrapper.appendChild(dropdown);

        editorConfig.container.appendChild(wrapper);

        var dropdownItems = [];
        var dropdownSelected = 0;
        var currentErrors = [];

// ////////////////////////////////////////////////////////////////////////

        function render() {

            // A trailing newline keeps the pre as tall as the textarea.
            display.innerHTML = highlighter(input.value) + '\n';
            renderGutter();
        }

// ////////////////////////////////////////////////////////////////////////

        function renderGutter() {

            $(gutter).empty();

            var lineCount = input.value.split('\n').length;

            var errorsByLine = {};
            for (var errorIdx = 0; errorIdx < currentErrors.length; errorIdx++) {
                errorsByLine[currentErrors[errorIdx].line] = currentErrors[errorIdx].message;
            }

            for (var lineIdx = 1; lineIdx <= lineCount; lineIdx++) {
                var line = document.createElement('div');
                line.className = 'mapper-editor-gutter-line';
                line.textContent = lineIdx;

                if (errorsByLine[lineIdx]) {
                    line.className = 'mapper-editor-gutter-line mapper-editor-gutter-line-error';
                    line.title = errorsByLine[lineIdx];
                }

                gutter.appendChild(line);
            }
        }

// ////////////////////////////////////////////////////////////////////////

        // The word being typed at the caret, used as the completion prefix.
        function tokenBeforeCaret() {

            var beforeCaret = input.value.substring(0, input.selectionStart);
            var match = beforeCaret.match(/[\w$.]+$/);

            if (match === null) {
                return '';
            }

            var out = match[0];
            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function closeDropdown() {
            dropdown.hidden = true;
            dropdownItems = [];
        }

// ////////////////////////////////////////////////////////////////////////

        function renderDropdown() {

            $(dropdown).empty();

            var lastCategory = '';

            for (var itemIdx = 0; itemIdx < dropdownItems.length; itemIdx++) {

                // Consecutive items of one category share one header row.
                var category = dropdownItems[itemIdx].category;
                if (category !== '' && category !== lastCategory) {
                    var header = document.createElement('li');
                    header.className = 'mapper-editor-completion-group';
                    header.textContent = category;
                    dropdown.appendChild(header);
                }
                lastCategory = category;

                var item = document.createElement('li');
                item.className = 'mapper-editor-completion';
                if (itemIdx === dropdownSelected) {
                    item.className = 'mapper-editor-completion mapper-editor-completion-selected';
                }
                item.setAttribute('data-index', itemIdx);

                var label = document.createElement('span');
                label.className = 'mapper-editor-completion-label';
                label.textContent = dropdownItems[itemIdx].label;
                item.appendChild(label);

                if (dropdownItems[itemIdx].doc !== '') {
                    var doc = document.createElement('span');
                    doc.className = 'mapper-editor-completion-doc';
                    doc.textContent = dropdownItems[itemIdx].doc;
                    item.appendChild(doc);
                }

                dropdown.appendChild(item);
            }

            dropdown.hidden = dropdownItems.length === 0;
        }

// ////////////////////////////////////////////////////////////////////////

        function openDropdown() {

            if (!editorConfig.completions) {
                return;
            }

            var token = tokenBeforeCaret();
            if (token === '') {
                closeDropdown();
                return;
            }

            // Case-insensitive prefix match over everything the caller offers.
            var tokenLower = token.toLowerCase();
            var all = editorConfig.completions();

            dropdownItems = [];
            for (var itemIdx = 0; itemIdx < all.length; itemIdx++) {
                var labelLower = all[itemIdx].label.toLowerCase();
                if (labelLower.indexOf(tokenLower) === 0) {
                    if (all[itemIdx].label !== token) {
                        dropdownItems.push(all[itemIdx]);
                    }
                }
                if (dropdownItems.length === config.autocompleteMaxItems) {
                    break;
                }
            }

            dropdownSelected = 0;
            renderDropdown();
        }

// ////////////////////////////////////////////////////////////////////////

        function acceptCompletion(itemIdx) {

            var token = tokenBeforeCaret();
            var caret = input.selectionStart;
            var chosen = dropdownItems[itemIdx].label;

            // Replace the token before the caret with the chosen completion.
            var beforeToken = input.value.substring(0, caret - token.length);
            var afterCaret = input.value.substring(caret);

            input.value = beforeToken + chosen + afterCaret;

            var newCaret = beforeToken.length + chosen.length;
            input.setSelectionRange(newCaret, newCaret);

            closeDropdown();
            render();
            editorConfig.onChange(input.value);
        }

// ////////////////////////////////////////////////////////////////////////

        $(input).on('input', function() {
            render();
            openDropdown();
            editorConfig.onChange(input.value);
        });

        $(input).on('scroll', function() {
            display.scrollTop = input.scrollTop;
            display.scrollLeft = input.scrollLeft;
            gutter.scrollTop = input.scrollTop;
        });

        $(input).on('keydown', function(event) {

            if (dropdown.hidden) {
                return;
            }

            if (event.key === 'ArrowDown') {
                event.preventDefault();
                dropdownSelected = (dropdownSelected + 1) % dropdownItems.length;
                renderDropdown();
            }
            else if (event.key === 'ArrowUp') {
                event.preventDefault();
                dropdownSelected = (dropdownSelected + dropdownItems.length - 1) % dropdownItems.length;
                renderDropdown();
            }
            else if (event.key === 'Enter' || event.key === 'Tab') {
                event.preventDefault();
                acceptCompletion(dropdownSelected);
            }
            else if (event.key === 'Escape') {
                closeDropdown();
            }
        });

        // Clicking a completion accepts it like Enter does.
        $(dropdown).on('mousedown', '.mapper-editor-completion', function(event) {
            event.preventDefault();
            acceptCompletion(parseInt($(this).attr('data-index'), 10));
        });

        $(input).on('blur', function() {
            closeDropdown();
        });

        input.value = editorConfig.value;
        render();

        return {

            getValue: function() {
                return input.value;
            },

            setValue: function(text) {
                input.value = text;
                closeDropdown();
                render();
            },

            // Errors are [{line, message}] records computed by the caller -
            // validation lives in the store, never in the editor.
            setErrors: function(errors) {
                currentErrors = errors;
                renderGutter();
            },

            focus: function() {
                input.focus();
            },

            element: wrapper
        };
    };

})(jQuery);
