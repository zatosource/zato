(function() {
    'use strict';

    /**
     * ZatoIDEEditorStatusbar - status bar component for the editor.
     * Renders status bar items with tooltips explaining each feature.
     * All state is per-instance, no global state stored.
     */
    var ZatoIDEEditorStatusbar = {

        /**
         * Status bar item definitions with placeholder descriptions.
         */
        items: {
            left: [
                {
                    id: 'position',
                    getValue: function(instance) {
                        return 'Ln ' + instance.cursorLine + ', Col ' + instance.cursorCol;
                    },
                    tooltip: 'Current cursor position - click to go to a specific line'
                },
                {
                    id: 'selection',
                    getValue: function(instance) {
                        if (instance.selectionLength > 0) {
                            return instance.selectionLength + ' selected';
                        }
                        return '';
                    },
                    tooltip: 'Number of characters currently selected'
                }
            ],
            right: [
                {
                    id: 'language',
                    getValue: function(instance) {
                        return ZatoIDEEditorStatusbar.getLanguageLabel(instance.options.language);
                    },
                    tooltip: 'Current syntax highlighting mode - click to change language'
                },
                {
                    id: 'encoding',
                    getValue: function() {
                        return 'UTF-8';
                    },
                    tooltip: 'File encoding - click to change encoding'
                },
                {
                    id: 'indentation',
                    getValue: function(instance) {
                        return 'Spaces: ' + instance.options.tabSize;
                    },
                    tooltip: 'Indentation settings - click to switch between tabs and spaces'
                },
                {
                    id: 'eol',
                    getValue: function() {
                        return 'LF';
                    },
                    tooltip: 'End of line sequence - click to change (LF, CRLF, CR)'
                }
            ]
        },

        /**
         * Language display labels.
         */
        languageLabels: {
            'python': 'Python',
            'sql': 'SQL',
            'yaml': 'YAML',
            'json': 'JSON',
            'ini': 'INI',
            'xml': 'XML',
            'html': 'HTML',
            'css': 'CSS',
            'javascript': 'JavaScript',
            'text': 'Plain text'
        },

        /**
         * Gets the display label for a language.
         */
        getLanguageLabel: function(language) {
            return this.languageLabels[language] || language;
        },

        /**
         * Renders the status bar into the instance's statusbar element.
         */
        render: function(instance) {
            var statusbar = instance.elements.statusbar;
            if (!statusbar) {
                return;
            }

            var html = '';
            html += '<div class="zato-ide-editor-statusbar-left">';
            html += this.renderItems(instance, this.items.left);
            html += '</div>';
            html += '<div class="zato-ide-editor-statusbar-right">';
            html += this.renderItems(instance, this.items.right);
            html += '</div>';

            statusbar.innerHTML = html;
            this.bindTooltips(instance);
        },

        /**
         * Renders a group of status bar items.
         */
        renderItems: function(instance, items) {
            var html = '';
            for (var i = 0; i < items.length; i++) {
                var item = items[i];
                var value = item.getValue(instance);
                if (value) {
                    html += '<span class="zato-ide-editor-statusbar-item" ';
                    html += 'data-item-id="' + item.id + '" ';
                    html += 'data-tooltip="' + this.escapeAttr(item.tooltip) + '">';
                    html += this.escapeHtml(value);
                    html += '</span>';
                }
            }
            return html;
        },

        /**
         * Updates just the position item without full re-render.
         */
        updatePosition: function(instance) {
            var statusbar = instance.elements.statusbar;
            if (!statusbar) {
                return;
            }

            var posItem = statusbar.querySelector('[data-item-id="position"]');
            if (posItem) {
                posItem.textContent = 'Ln ' + instance.cursorLine + ', Col ' + instance.cursorCol;
            }
        },

        /**
         * Updates the selection count display.
         */
        updateSelection: function(instance, length) {
            instance.selectionLength = length;
            var statusbar = instance.elements.statusbar;
            if (!statusbar) {
                return;
            }

            var selItem = statusbar.querySelector('[data-item-id="selection"]');
            if (length > 0) {
                if (selItem) {
                    selItem.textContent = length + ' selected';
                    selItem.style.display = '';
                } else {
                    this.render(instance);
                }
            } else {
                if (selItem) {
                    selItem.style.display = 'none';
                }
            }
        },

        /**
         * Updates the language display.
         */
        updateLanguage: function(instance) {
            var statusbar = instance.elements.statusbar;
            if (!statusbar) {
                return;
            }

            var langItem = statusbar.querySelector('[data-item-id="language"]');
            if (langItem) {
                langItem.textContent = this.getLanguageLabel(instance.options.language);
            }
        },

        /**
         * Binds tooltip events to the statusbar using ZatoTooltip.
         */
        bindTooltips: function(instance) {
            var statusbar = instance.elements.statusbar;
            if (!statusbar) {
                return;
            }

            if (!statusbar.id) {
                statusbar.id = 'zato-ide-statusbar-' + instance.id;
            }

            if (instance.tooltipInstance) {
                ZatoTooltip.destroy(statusbar.id);
            }

            instance.tooltipInstance = ZatoTooltip.create(statusbar.id, {
                theme: 'dark',
                attribute: 'data-tooltip'
            });
        },

        /**
         * Hides the active tooltip for the instance.
         */
        hideTooltip: function(instance) {
            if (instance.tooltipInstance) {
                ZatoTooltip.hide(instance.tooltipInstance);
            }
        },

        /**
         * Escapes HTML entities.
         */
        escapeHtml: function(text) {
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        /**
         * Escapes attribute value.
         */
        escapeAttr: function(text) {
            return text.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
        }
    };

    window.ZatoIDEEditorStatusbar = ZatoIDEEditorStatusbar;

})();
