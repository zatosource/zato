(function() {
    'use strict';

    var ZatoIDESymbolNav = {

        updateSymbols: function(instance) {
            if (!instance.symbolDropdown || !window.ZatoIDESymbols) {
                return;
            }

            var file = instance.files[instance.activeFile];
            if (!file) {
                return;
            }

            var symbols = ZatoIDESymbols.extract(file.content, file.language);
            instance.cachedSymbols = symbols;
            var container = instance.symbolDropdown;
            var menu = container.querySelector('.zato-dropdown-menu');
            var textSpan = container.querySelector('.zato-dropdown-text');

            if (!menu) {
                return;
            }

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
                if (textSpan) {
                    textSpan.textContent = '-- symbols --';
                }
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

            if (textSpan) {
                textSpan.textContent = symbols[0].name;
            }
            container.setAttribute('data-value', symbols[0].line);

            instance.selectedClassLine = symbols[0].line;
            this.updateMethods(instance, symbols[0].line);
        },

        syncDropdownsToLine: function(instance, line) {
            if (!instance.symbolDropdown) {
                return;
            }

            var cachedSymbols = instance.cachedSymbols || [];
            var cachedMethods = instance.cachedMethods || [];
            var symbolContainer = instance.symbolDropdown;
            var symbolTextSpan = symbolContainer.querySelector('.zato-dropdown-text');

            if (cachedSymbols.length === 0) {
                return;
            }

            var file = instance.files[instance.activeFile];
            var lineCount = file && file.content ? file.content.split('\n').length : 1;
            var firstSymbolLine = cachedSymbols[0].line;
            var lastSymbolLine = cachedSymbols[cachedSymbols.length - 1].line;

            if (line < firstSymbolLine) {
                if (symbolTextSpan) {
                    symbolTextSpan.textContent = '(top)';
                }
                symbolContainer.setAttribute('data-value', '1');
                instance.selectedClassLine = null;
                if (instance.methodDropdown) {
                    instance.methodDropdown.style.display = 'none';
                }
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
                } else {
                    break;
                }
            }

            var symbolEnd = symbol ? this.estimateSymbolEnd(file.content, symbol.line) : null;

            var isOutsideSymbol = false;
            if (symbol && symbolEnd !== null && line >= symbolEnd) {
                isOutsideSymbol = true;
            }

            if (symbol && nextSymbolLine === null && line > lastSymbolLine) {
                var lastSymbolMethods = ZatoIDESymbols.extractMethods(file.content, file.language, lastSymbolLine);
                var lastMethodLine = lastSymbolMethods.length > 0 ? lastSymbolMethods[lastSymbolMethods.length - 1].line : lastSymbolLine;
                var estimatedEnd = this.estimateSymbolEnd(file.content, lastMethodLine);
                if (line > estimatedEnd) {
                    if (symbolTextSpan) {
                        symbolTextSpan.textContent = '(bottom)';
                    }
                    symbolContainer.setAttribute('data-value', lineCount);
                    instance.selectedClassLine = null;
                    if (instance.methodDropdown) {
                        instance.methodDropdown.style.display = 'none';
                    }
                    return;
                }
            }

            if (isOutsideSymbol) {
                if (instance.methodDropdown) {
                    instance.methodDropdown.style.display = 'none';
                }
                return;
            }

            if (instance.selectedClassLine !== symbol.line) {
                instance.selectedClassLine = symbol.line;
                this.updateMethods(instance, symbol.line);
                cachedMethods = instance.cachedMethods || [];
            }

            if (symbolTextSpan) {
                symbolTextSpan.textContent = symbol.name;
            }
            symbolContainer.setAttribute('data-value', symbol.line);

            var method = null;
            var methodIndex = -1;
            var nextMethodLine = null;
            for (var j = 0; j < cachedMethods.length; j++) {
                if (cachedMethods[j].line <= line) {
                    method = cachedMethods[j];
                    methodIndex = j;
                    nextMethodLine = (j + 1 < cachedMethods.length) ? cachedMethods[j + 1].line : null;
                } else {
                    break;
                }
            }

            var isOutsideMethod = false;
            if (method) {
                var methodEnd = this.estimateSymbolEnd(file.content, method.line);
                if (line >= methodEnd) {
                    isOutsideMethod = true;
                }
            } else {
                if (cachedMethods.length > 0 && line < cachedMethods[0].line) {
                    isOutsideMethod = true;
                }
            }

            if (instance.methodDropdown) {
                var methodContainer = instance.methodDropdown;
                var methodTextSpan = methodContainer.querySelector('.zato-dropdown-text');

                if (!method) {
                } else if (isOutsideMethod) {
                } else {
                    if (methodTextSpan) {
                        methodTextSpan.textContent = method.name;
                    }
                    methodContainer.setAttribute('data-value', method.line);
                }
            }
        },

        estimateSymbolEnd: function(content, startLine) {
            var lines = content.split('\n');
            var startIndex = startLine - 1;
            if (startIndex < 0 || startIndex >= lines.length) {
                return startLine;
            }

            var baseIndent = this.getIndent(lines[startIndex]);

            for (var i = startIndex + 1; i < lines.length; i++) {
                var line = lines[i];
                var trimmed = line.trim();
                if (trimmed === '') {
                    continue;
                }
                var currentIndent = this.getIndent(line);
                if (currentIndent <= baseIndent) {
                    return i;
                }
            }
            return lines.length;
        },

        getIndent: function(line) {
            var match = line.match(/^(\s*)/);
            return match ? match[1].length : 0;
        },

        updateMethods: function(instance, classLine) {
            if (!instance.methodDropdown || !window.ZatoIDESymbols) {
                return;
            }

            var file = instance.files[instance.activeFile];
            if (!file) {
                return;
            }

            var methods = ZatoIDESymbols.extractMethods(file.content, file.language, classLine);
            instance.cachedMethods = methods;

            var container = instance.methodDropdown;
            var menu = container.querySelector('.zato-dropdown-menu');
            var textSpan = container.querySelector('.zato-dropdown-text');

            if (!menu) {
                return;
            }

            menu.innerHTML = '';

            if (methods.length === 0) {
                container.style.display = 'none';
                return;
            }

            container.style.display = '';

            for (var i = 0; i < methods.length; i++) {
                var method = methods[i];
                var item = document.createElement('div');
                item.className = 'zato-dropdown-item';
                item.setAttribute('data-value', method.line);
                item.textContent = method.name;
                menu.appendChild(item);
            }

            if (textSpan) {
                textSpan.textContent = methods[0].name;
            }
            container.setAttribute('data-value', methods[0].line);
        },

        jumpToLine: function(instance, line) {
            if (!instance.codeEditor) {
                return;
            }

            var targetLine = Math.max(1, line - 2);
            ZatoIDEEditorAce.scrollToLine(instance.codeEditor, targetLine);
        }
    };

    window.ZatoIDESymbolNav = ZatoIDESymbolNav;

})();
