(function() {
    'use strict';

    /**
     * ZatoIDEEditor - reusable code editor component with syntax highlighting.
     *
     * Usage:
     *   var editor = ZatoIDEEditor.create(containerElement, {
     *       theme: 'dark',
     *       language: 'python',
     *       content: 'print("Hello")',
     *       onContentChange: function(content) { ... },
     *       onCursorChange: function(line, col) { ... }
     *   });
     *
     *   ZatoIDEEditor.setValue(editor, 'new content');
     *   var content = ZatoIDEEditor.getValue(editor);
     *   ZatoIDEEditor.setLanguage(editor, 'sql');
     *   ZatoIDEEditor.setTheme(editor, 'light');
     *   ZatoIDEEditor.destroy(editor);
     */
    var ZatoIDEEditor = {

        instances: {},

        defaultOptions: {
            theme: 'dark',
            language: 'python',
            fontSize: 13,
            tabSize: 4,
            lineHeight: 1.5,
            cursorBlinkRate: 530
        },

        /**
         * Creates a new editor instance inside the given container element.
         */
        create: function(container, options) {
            console.log('[ZatoIDEEditor] create: starting');
            var self = this;
            var opts = {};
            var key;

            for (key in this.defaultOptions) {
                opts[key] = this.defaultOptions[key];
            }
            for (key in options) {
                opts[key] = options[key];
            }

            var instanceId = 'zato-ide-editor-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
            console.log('[ZatoIDEEditor] create: instanceId=' + instanceId);

            var instance = {
                id: instanceId,
                container: container,
                options: opts,
                content: opts.content || '',
                cursorLine: 1,
                cursorCol: 1,
                scrollTop: 0,
                scrollLeft: 0,
                selection: null,
                focused: false,
                lines: [],
                elements: {}
            };

            console.log('[ZatoIDEEditor] create: calling render');
            this.render(instance);
            console.log('[ZatoIDEEditor] create: calling bindEvents');
            this.bindEvents(instance);
            this.instances[instanceId] = instance;

            if (instance.content) {
                console.log('[ZatoIDEEditor] create: setting initial content, length=' + instance.content.length);
                this.setContent(instance, instance.content);
            }

            console.log('[ZatoIDEEditor] create: complete');
            return instance;
        },

        /**
         * Renders the editor HTML structure.
         */
        render: function(instance) {
            console.log('[ZatoIDEEditor] render: starting, theme=' + instance.options.theme);
            var themeClass = 'zato-ide-editor-theme-' + instance.options.theme;
            var container = instance.container;
            console.log('[ZatoIDEEditor] render: container=' + (container ? 'found' : 'null'));

            container.innerHTML = '';
            container.className = 'zato-ide-editor-wrapper ' + themeClass;

            var editorEl = document.createElement('div');
            editorEl.className = 'zato-ide-editor-main';
            editorEl.setAttribute('tabindex', '0');

            var gutterEl = document.createElement('div');
            gutterEl.className = 'zato-ide-editor-gutter';

            var contentWrapper = document.createElement('div');
            contentWrapper.className = 'zato-ide-editor-content-wrapper';

            var codeEl = document.createElement('div');
            codeEl.className = 'zato-ide-editor-code';

            var textarea = document.createElement('textarea');
            textarea.className = 'zato-ide-editor-textarea';
            textarea.setAttribute('spellcheck', 'false');
            textarea.setAttribute('autocomplete', 'off');
            textarea.setAttribute('autocorrect', 'off');
            textarea.setAttribute('autocapitalize', 'off');

            var cursorEl = document.createElement('div');
            cursorEl.className = 'zato-ide-editor-cursor';

            var highlightLayer = document.createElement('div');
            highlightLayer.className = 'zato-ide-editor-highlight-layer';

            var lineHighlight = document.createElement('div');
            lineHighlight.className = 'zato-ide-editor-line-highlight';

            var selectionOverlay = document.createElement('div');
            selectionOverlay.className = 'zato-ide-editor-selection-overlay';

            var statusbar = document.createElement('div');
            statusbar.className = 'zato-ide-editor-statusbar';

            contentWrapper.appendChild(lineHighlight);
            contentWrapper.appendChild(selectionOverlay);
            contentWrapper.appendChild(highlightLayer);
            contentWrapper.appendChild(codeEl);
            contentWrapper.appendChild(textarea);
            contentWrapper.appendChild(cursorEl);

            editorEl.appendChild(gutterEl);
            editorEl.appendChild(contentWrapper);

            container.appendChild(editorEl);
            container.appendChild(statusbar);

            instance.elements = {
                editor: editorEl,
                gutter: gutterEl,
                contentWrapper: contentWrapper,
                code: codeEl,
                textarea: textarea,
                cursor: cursorEl,
                highlightLayer: highlightLayer,
                lineHighlight: lineHighlight,
                selectionOverlay: selectionOverlay,
                statusbar: statusbar
            };

            console.log('[ZatoIDEEditor] render: elements created, applying styles');
            this.applyStyles(instance);
            console.log('[ZatoIDEEditor] render: rendering statusbar');
            ZatoIDEEditorStatusbar.render(instance);
            console.log('[ZatoIDEEditor] render: complete');
        },

        /**
         * Applies font size and line height styles.
         */
        applyStyles: function(instance) {
            var opts = instance.options;
            var els = instance.elements;

            els.code.style.fontSize = opts.fontSize + 'px';
            els.code.style.lineHeight = opts.lineHeight;
            els.textarea.style.fontSize = opts.fontSize + 'px';
            els.textarea.style.lineHeight = opts.lineHeight;
            els.gutter.style.fontSize = opts.fontSize + 'px';
            els.gutter.style.lineHeight = opts.lineHeight;
        },

        /**
         * Binds all event listeners.
         */
        bindEvents: function(instance) {
            var self = this;
            var textarea = instance.elements.textarea;
            var editor = instance.elements.editor;
            var contentWrapper = instance.elements.contentWrapper;

            textarea.addEventListener('input', function() {
                self.handleInput(instance);
            });

            textarea.addEventListener('keydown', function(e) {
                self.handleKeydown(instance, e);
            });

            textarea.addEventListener('click', function() {
                self.updateCursorPosition(instance);
                self.updateSelectionOverlay(instance);
            });

            textarea.addEventListener('keyup', function() {
                self.updateCursorPosition(instance);
                self.updateSelectionOverlay(instance);
            });

            textarea.addEventListener('focus', function() {
                instance.focused = true;
                self.startCursorBlink(instance);
                editor.classList.add('focused');
            });

            textarea.addEventListener('blur', function() {
                instance.focused = false;
                self.stopCursorBlink(instance);
                editor.classList.remove('focused');
                self.clearSelectionOverlay(instance);
            });

            textarea.addEventListener('scroll', function() {
                self.syncScroll(instance);
            });

            textarea.addEventListener('select', function() {
                console.log('[SELECTION] select event fired');
                self.updateSelectionOverlay(instance);
            });

            textarea.addEventListener('mouseup', function() {
                console.log('[SELECTION] mouseup event fired');
                self.updateSelectionOverlay(instance);
            });

            textarea.addEventListener('mousemove', function(e) {
                if (e.buttons === 1) {
                    console.log('[SELECTION] mousemove with button down');
                    self.updateSelectionOverlay(instance);
                }
            });

            editor.addEventListener('click', function() {
                textarea.focus();
            });
        },

        /**
         * Handles text input.
         */
        handleInput: function(instance) {
            var textarea = instance.elements.textarea;
            instance.content = textarea.value;
            this.updateDisplay(instance);
            this.updateCursorPosition(instance);

            if (instance.options.onContentChange) {
                instance.options.onContentChange(instance.content);
            }
        },

        /**
         * Handles special keys like Tab.
         */
        handleKeydown: function(instance, e) {
            if (e.key === 'Tab') {
                e.preventDefault();
                var textarea = instance.elements.textarea;
                var start = textarea.selectionStart;
                var end = textarea.selectionEnd;
                var spaces = '';
                for (var i = 0; i < instance.options.tabSize; i++) {
                    spaces += ' ';
                }
                textarea.value = textarea.value.substring(0, start) + spaces + textarea.value.substring(end);
                textarea.selectionStart = textarea.selectionEnd = start + instance.options.tabSize;
                this.handleInput(instance);
            }
        },

        /**
         * Updates the syntax-highlighted display.
         */
        updateDisplay: function(instance) {
            console.log('[ZatoIDEEditor] updateDisplay: starting, language=' + instance.options.language);
            var content = instance.content || '';
            var lines = content.split('\n');
            instance.lines = lines;
            console.log('[ZatoIDEEditor] updateDisplay: lineCount=' + lines.length);

            var highlightedHtml = ZatoIDEEditorHighlight.highlight(content, instance.options.language);
            console.log('[ZatoIDEEditor] updateDisplay: highlighted, htmlLength=' + highlightedHtml.length);
            instance.elements.code.innerHTML = highlightedHtml;

            ZatoIDEEditorGutter.render(instance, lines.length);
            console.log('[ZatoIDEEditor] updateDisplay: complete');
        },

        /**
         * Updates cursor position based on textarea selection.
         */
        updateCursorPosition: function(instance) {
            var textarea = instance.elements.textarea;
            var value = textarea.value;
            var pos = textarea.selectionStart;

            var textBefore = value.substring(0, pos);
            var lines = textBefore.split('\n');
            var line = lines.length;
            var col = lines[lines.length - 1].length + 1;

            instance.cursorLine = line;
            instance.cursorCol = col;

            ZatoIDEEditorCursor.updatePosition(instance, line, col);
            ZatoIDEEditorGutter.highlightLine(instance, line);

            ZatoIDEEditorStatusbar.updatePosition(instance);

            if (instance.options.onCursorChange) {
                instance.options.onCursorChange(line, col);
            }
        },

        /**
         * Scrolls the editor to a specific line.
         */
        scrollToLine: function(instance, line) {
            console.log('[TRACE-SYMBOL] editor.scrollToLine: called with line=' + line);
            var textarea = instance.elements.textarea;
            if (!textarea) {
                console.log('[TRACE-SYMBOL] editor.scrollToLine: no textarea, aborting');
                return;
            }

            var lineCount = instance.content.split('\n').length;
            var scrollHeight = textarea.scrollHeight;
            var lineHeightPx = scrollHeight / lineCount;
            var targetScrollTop = (line - 1) * lineHeightPx;
            console.log('[TRACE-SYMBOL] editor.scrollToLine: lineCount=' + lineCount + ', scrollHeight=' + scrollHeight + ', lineHeightPx=' + lineHeightPx);
            console.log('[TRACE-SYMBOL] editor.scrollToLine: targetScrollTop=' + targetScrollTop + ' ((line=' + line + ' - 1) * lineHeightPx=' + lineHeightPx + ')');
            console.log('[TRACE-SYMBOL] editor.scrollToLine: textarea.scrollTop BEFORE=' + textarea.scrollTop);

            textarea.scrollTop = targetScrollTop;
            console.log('[TRACE-SYMBOL] editor.scrollToLine: textarea.scrollTop AFTER=' + textarea.scrollTop);
            console.log('[TRACE-SYMBOL] editor.scrollToLine: textarea.clientHeight=' + textarea.clientHeight);
            this.syncScroll(instance);
            console.log('[TRACE-SYMBOL] editor.scrollToLine: syncScroll called');
        },

        /**
         * Syncs scroll position between textarea and display layers.
         */
        syncScroll: function(instance) {
            var textarea = instance.elements.textarea;
            var code = instance.elements.code;
            var gutter = instance.elements.gutter;
            var highlightLayer = instance.elements.highlightLayer;
            var lineHighlight = instance.elements.lineHighlight;
            var selectionOverlay = instance.elements.selectionOverlay;

            code.scrollTop = textarea.scrollTop;
            code.scrollLeft = textarea.scrollLeft;
            gutter.scrollTop = textarea.scrollTop;
            highlightLayer.scrollTop = textarea.scrollTop;
            highlightLayer.scrollLeft = textarea.scrollLeft;
            selectionOverlay.scrollTop = textarea.scrollTop;

            instance.scrollTop = textarea.scrollTop;
            instance.scrollLeft = textarea.scrollLeft;

            ZatoIDEEditorCursor.updatePosition(instance, instance.cursorLine, instance.cursorCol);
        },

        /**
         * Starts cursor blinking.
         */
        startCursorBlink: function(instance) {
            ZatoIDEEditorCursor.startBlink(instance);
        },

        /**
         * Stops cursor blinking.
         */
        stopCursorBlink: function(instance) {
            ZatoIDEEditorCursor.stopBlink(instance);
        },

        /**
         * Sets editor content.
         */
        setContent: function(instance, content) {
            instance.content = content;
            instance.elements.textarea.value = content;
            this.updateDisplay(instance);
            this.updateCursorPosition(instance);
        },

        /**
         * Gets editor content.
         */
        getValue: function(instance) {
            return instance ? instance.content : '';
        },

        /**
         * Sets editor content (alias for setContent).
         */
        setValue: function(instance, value) {
            this.setContent(instance, value);
        },

        /**
         * Sets the syntax highlighting language.
         */
        setLanguage: function(instance, language) {
            instance.options.language = language;
            this.updateDisplay(instance);
        },

        /**
         * Sets the editor theme.
         */
        setTheme: function(instance, theme) {
            instance.options.theme = theme;
            var themeClass = 'zato-ide-editor-theme-' + theme;
            instance.container.className = 'zato-ide-editor-wrapper ' + themeClass;
        },

        /**
         * Focuses the editor.
         */
        focus: function(instance) {
            if (instance && instance.elements.textarea) {
                instance.elements.textarea.focus();
            }
        },

        /**
         * Gets an instance by ID.
         */
        getInstance: function(instanceId) {
            return this.instances[instanceId] || null;
        },

        /**
         * Destroys an editor instance.
         */
        destroy: function(instance) {
            if (!instance) {
                return;
            }
            this.stopCursorBlink(instance);
            instance.container.innerHTML = '';
            delete this.instances[instance.id];
        },

        /**
         * Updates the selection overlay to show full-width line backgrounds.
         */
        updateSelectionOverlay: function(instance) {
            var textarea = instance.elements.textarea;
            var overlay = instance.elements.selectionOverlay;
            var code = instance.elements.code;
            if (!textarea || !overlay || !code) {
                return;
            }

            var start = textarea.selectionStart;
            var end = textarea.selectionEnd;

            if (start === end) {
                overlay.innerHTML = '';
                return;
            }

            var value = textarea.value;

            var textBefore = value.substring(0, start);
            var startLine = textBefore.split('\n').length;
            var startCol = start - textBefore.lastIndexOf('\n') - 1;

            var textToEnd = value.substring(0, end);
            var endLine = textToEnd.split('\n').length;
            var endCol = end - textToEnd.lastIndexOf('\n') - 1;

            var lines = value.split('\n');

            var lineElements = code.querySelectorAll('.zato-ide-editor-line');
            if (lineElements.length === 0) {
                return;
            }

            var firstLineEl = lineElements[0];
            var lineHeightPx = firstLineEl.offsetHeight;

            var charWidthPx = this.getCharWidth(instance);

            var html = '';
            for (var i = startLine; i <= endLine; i++) {
                var top = (i - 1) * lineHeightPx;
                var lineText = lines[i - 1] || '';
                var lineLen = lineText.length;

                var leftCol = 0;
                var rightCol = lineLen;

                if (i === startLine) {
                    leftCol = startCol;
                }
                if (i === endLine) {
                    rightCol = endCol;
                }

                var left = leftCol * charWidthPx;
                var width = (rightCol - leftCol) * charWidthPx;

                if (width <= 0 && i !== endLine) {
                    width = charWidthPx;
                }

                if (width > 0 || (i > startLine && i < endLine)) {
                    if (i > startLine && i < endLine) {
                        html += '<div class="zato-ide-editor-selection-line" style="top:' + top + 'px;height:' + lineHeightPx + 'px;left:0;right:0;"></div>';
                    } else {
                        html += '<div class="zato-ide-editor-selection-line" style="top:' + top + 'px;height:' + lineHeightPx + 'px;left:' + left + 'px;width:' + width + 'px;"></div>';
                    }
                }
            }

            overlay.innerHTML = html;
        },

        getCharWidth: function(instance) {
            var code = instance.elements.code;
            if (!code) {
                return 8;
            }

            var span = document.createElement('span');
            span.style.visibility = 'hidden';
            span.style.position = 'absolute';
            span.style.whiteSpace = 'pre';
            span.textContent = 'M';
            code.appendChild(span);
            var width = span.offsetWidth;
            code.removeChild(span);
            return width || 8;
        },

        /**
         * Clears the selection overlay.
         */
        clearSelectionOverlay: function(instance) {
            var overlay = instance.elements.selectionOverlay;
            if (overlay) {
                overlay.innerHTML = '';
            }
        }
    };

    window.ZatoIDEEditor = ZatoIDEEditor;

})();
