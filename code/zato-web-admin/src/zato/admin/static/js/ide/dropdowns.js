(function() {
    'use strict';

    var ZatoIDEDropdowns = {

        initDropdowns: function(instance) {
            var self = this;

            var symbolSelect = document.getElementById(instance.id + '-symbol-select');
            if (symbolSelect && typeof ZatoDropdown !== 'undefined') {
                instance.symbolDropdown = ZatoDropdown.init(symbolSelect, {
                    theme: instance.options.theme,
                    id: instance.id + '-symbol-dropdown',
                    onBeforeOpen: function(container) {
                        var menu = container.querySelector('.zato-dropdown-menu');
                        var trigger = container.querySelector('.zato-dropdown-trigger');
                        if (menu && trigger) {
                            var rect = trigger.getBoundingClientRect();
                            menu.style.position = 'fixed';
                            menu.style.bottom = 'auto';
                            menu.style.left = rect.left + 'px';
                            menu.style.top = (rect.bottom + 2) + 'px';
                            menu.style.minWidth = rect.width + 'px';
                        }
                    },
                    onChange: function(value, text) {
                        if (value) {
                            var line = parseInt(value, 10);
                            self.jumpToLine(instance, line);
                            instance.selectedClassLine = line;
                            self.updateMethods(instance, line);
                        }
                    }
                });
            }

            var methodSelect = document.getElementById(instance.id + '-method-select');
            if (methodSelect && typeof ZatoDropdown !== 'undefined') {
                instance.methodDropdown = ZatoDropdown.init(methodSelect, {
                    theme: instance.options.theme,
                    id: instance.id + '-method-dropdown',
                    onBeforeOpen: function(container) {
                        var menu = container.querySelector('.zato-dropdown-menu');
                        var trigger = container.querySelector('.zato-dropdown-trigger');
                        if (menu && trigger) {
                            var rect = trigger.getBoundingClientRect();
                            menu.style.position = 'fixed';
                            menu.style.bottom = 'auto';
                            menu.style.left = rect.left + 'px';
                            menu.style.top = (rect.bottom + 2) + 'px';
                            menu.style.minWidth = rect.width + 'px';
                        }
                    },
                    onChange: function(value, text) {
                        console.log('[TRACE-METHOD] dropdown.onChange: value="' + value + '" text="' + text + '"');
                        if (value) {
                            var line = parseInt(value, 10);
                            self.jumpToLine(instance, line);
                        }
                    }
                });
            }

            var debugSelect = document.getElementById(instance.id + '-debug-select');
            if (debugSelect && typeof ZatoDropdown !== 'undefined') {
                instance.debugDropdown = ZatoDropdown.init(debugSelect, {
                    theme: instance.options.theme,
                    id: instance.id + '-debug-dropdown',
                    onBeforeOpen: function(container) {
                        var menu = container.querySelector('.zato-dropdown-menu');
                        var trigger = container.querySelector('.zato-dropdown-trigger');
                        if (menu && trigger) {
                            var rect = trigger.getBoundingClientRect();
                            menu.style.position = 'fixed';
                            menu.style.bottom = 'auto';
                            menu.style.left = rect.left + 'px';
                            menu.style.top = (rect.bottom + 2) + 'px';
                            menu.style.minWidth = rect.width + 'px';
                        }
                    },
                    onChange: function(value, text) {
                        if (value) {
                            ZatoIDE.handleDebugAction(instance, value);
                            if (instance.debugDropdown) {
                                ZatoDropdown.setValue(instance.debugDropdown, '');
                            }
                        }
                    }
                });
            }
        },

        updateSymbols: function(instance) {
            if (!instance.symbolDropdown || !window.ZatoIDESymbols) { return; }
            var file = instance.files[instance.activeFile];
            if (!file) { return; }
            var symbols = ZatoIDESymbols.extract(file.content, file.language);
            instance.cachedSymbols = symbols;
            var container = instance.symbolDropdown;
            var menu = container.querySelector('.zato-dropdown-menu');
            var textSpan = container.querySelector('.zato-dropdown-text');
            if (!menu) { return; }
            menu.innerHTML = '';
            var lineCount = file.content ? file.content.split('\n').length : 1;
            if (symbols.length > 0) {
                var topItem = document.createElement('div');
                topItem.className = 'zato-dropdown-item';
                topItem.setAttribute('data-value', '1');
                topItem.textContent = '(top)';
                menu.appendChild(topItem);
                var bottomItem = document.createElement('div');
                bottomItem.className = 'zato-dropdown-item';
                bottomItem.setAttribute('data-value', lineCount);
                bottomItem.textContent = '(bottom)';
                menu.appendChild(bottomItem);
                var separator = document.createElement('div');
                separator.className = 'zato-dropdown-separator';
                menu.appendChild(separator);
            }
            if (symbols.length === 0) {
                var emptyItem = document.createElement('div');
                emptyItem.className = 'zato-dropdown-item disabled';
                emptyItem.textContent = '(no symbols)';
                menu.appendChild(emptyItem);
                if (textSpan) { textSpan.textContent = '-- symbols --'; }
                return;
            }
            for (var i = 0; i < symbols.length; i++) {
                var symbol = symbols[i];
                var item = document.createElement('div');
                item.className = 'zato-dropdown-item';
                item.setAttribute('data-value', symbol.line);
                item.textContent = symbol.name;
                menu.appendChild(item);
            }
            if (textSpan) { textSpan.textContent = symbols[0].name; }
            container.setAttribute('data-value', symbols[0].line);
            instance.selectedClassLine = symbols[0].line;
            this.updateMethods(instance, symbols[0].line);
        },

        syncDropdownsToLine: function(instance, line) {
            if (!instance.symbolDropdown) { return; }
            var cachedSymbols = instance.cachedSymbols || [];
            var cachedMethods = instance.cachedMethods || [];
            var symbolContainer = instance.symbolDropdown;
            var symbolTextSpan = symbolContainer.querySelector('.zato-dropdown-text');
            if (cachedSymbols.length === 0) { return; }
            var file = instance.files[instance.activeFile];
            var lineCount = file && file.content ? file.content.split('\n').length : 1;
            var firstSymbolLine = cachedSymbols[0].line;
            var lastSymbolLine = cachedSymbols[cachedSymbols.length - 1].line;
            if (line < firstSymbolLine) {
                if (symbolTextSpan) { symbolTextSpan.textContent = '(top)'; }
                symbolContainer.setAttribute('data-value', '1');
                instance.selectedClassLine = null;
                if (instance.methodDropdown) { instance.methodDropdown.style.display = 'none'; }
                return;
            }
            var symbol = null;
            var symbolIndex = -1;
            var nextSymbolLine = null;
            for (var i = 0; i < cachedSymbols.length; i++) {
                if (cachedSymbols[i].line <= line) {
                    symbol = cachedSymbols[i];
                    symbolIndex = i;
                    nextSymbolLine = (i + 1 < cachedSymbols.length) ? cachedSymbols[i + 1].line : null;
                } else { break; }
            }
            var symbolEnd = symbol ? this.estimateSymbolEnd(file.content, symbol.line) : null;
            var isOutsideSymbol = (symbol && symbolEnd !== null && line >= symbolEnd);
            if (symbol && nextSymbolLine === null && line > lastSymbolLine) {
                var lastSymbolMethods = ZatoIDESymbols.extractMethods(file.content, file.language, lastSymbolLine);
                var lastMethodLine = lastSymbolMethods.length > 0 ? lastSymbolMethods[lastSymbolMethods.length - 1].line : lastSymbolLine;
                var estimatedEnd = this.estimateSymbolEnd(file.content, lastMethodLine);
                if (line > estimatedEnd) {
                    if (symbolTextSpan) { symbolTextSpan.textContent = '(bottom)'; }
                    symbolContainer.setAttribute('data-value', lineCount);
                    instance.selectedClassLine = null;
                    if (instance.methodDropdown) { instance.methodDropdown.style.display = 'none'; }
                    return;
                }
            }
            if (isOutsideSymbol) {
                if (instance.methodDropdown) { instance.methodDropdown.style.display = 'none'; }
                return;
            }
            if (instance.selectedClassLine !== symbol.line) {
                instance.selectedClassLine = symbol.line;
                this.updateMethods(instance, symbol.line);
                cachedMethods = instance.cachedMethods || [];
            }
            if (symbolTextSpan) { symbolTextSpan.textContent = symbol.name; }
            symbolContainer.setAttribute('data-value', symbol.line);
            var method = null;
            var methodIndex = -1;
            var nextMethodLine = null;
            for (var j = 0; j < cachedMethods.length; j++) {
                if (cachedMethods[j].line <= line) {
                    method = cachedMethods[j];
                    methodIndex = j;
                    nextMethodLine = (j + 1 < cachedMethods.length) ? cachedMethods[j + 1].line : null;
                } else { break; }
            }
            var isOutsideMethod = false;
            if (method) {
                var methodEnd = this.estimateSymbolEnd(file.content, method.line);
                if (line >= methodEnd) { isOutsideMethod = true; }
            } else {
                if (cachedMethods.length > 0 && line < cachedMethods[0].line) { isOutsideMethod = true; }
            }
            if (instance.methodDropdown && method && !isOutsideMethod) {
                var methodContainer = instance.methodDropdown;
                var methodTextSpan = methodContainer.querySelector('.zato-dropdown-text');
                if (methodTextSpan) { methodTextSpan.textContent = method.name; }
                methodContainer.setAttribute('data-value', method.line);
            }
        },

        estimateSymbolEnd: function(content, startLine) {
            var lines = content.split('\n');
            var startIndex = startLine - 1;
            if (startIndex < 0 || startIndex >= lines.length) { return startLine; }
            var baseIndent = this.getIndent(lines[startIndex]);
            for (var i = startIndex + 1; i < lines.length; i++) {
                var line = lines[i];
                if (line.trim() === '') { continue; }
                if (this.getIndent(line) <= baseIndent) { return i; }
            }
            return lines.length;
        },

        getIndent: function(line) {
            var match = line.match(/^(\s*)/);
            return match ? match[1].length : 0;
        },

        updateMethods: function(instance, classLine) {
            if (!instance.methodDropdown || !window.ZatoIDESymbols) { return; }
            var file = instance.files[instance.activeFile];
            if (!file) { return; }
            var methods = ZatoIDESymbols.extractMethods(file.content, file.language, classLine);
            instance.cachedMethods = methods;
            var container = instance.methodDropdown;
            var menu = container.querySelector('.zato-dropdown-menu');
            var textSpan = container.querySelector('.zato-dropdown-text');
            if (!menu) { return; }
            menu.innerHTML = '';
            if (methods.length === 0) { container.style.display = 'none'; return; }
            container.style.display = '';
            for (var i = 0; i < methods.length; i++) {
                var method = methods[i];
                var item = document.createElement('div');
                item.className = 'zato-dropdown-item';
                item.setAttribute('data-value', method.line);
                item.textContent = method.name;
                menu.appendChild(item);
            }
            if (textSpan) { textSpan.textContent = methods[0].name; }
            container.setAttribute('data-value', methods[0].line);
        },

        jumpToLine: function(instance, line) {
            if (!instance.codeEditor) { return; }
            var targetLine = Math.max(1, line - 2);
            ZatoIDEEditorAce.scrollToLine(instance.codeEditor, targetLine);
        }
    };

    window.ZatoIDEDropdowns = ZatoIDEDropdowns;

})();
