(function() {
    'use strict';

    var ZatoIDELocalSymbols = {

        parseDebounceMs: 100,

        create: function(editor, instance) {
            var self = this;

            instance.localSymbols = {
                classes: {},
                functions: {},
                variables: {},
                imports: {},
                occurrences: {},
                parseTimeout: null
            };

            self.parseFile(editor, instance);

            editor.session.on('change', function() {
                self.scheduleReparse(editor, instance);
            });

            return instance.localSymbols;
        },

        scheduleReparse: function(editor, instance) {
            var self = this;

            if (instance.localSymbols.parseTimeout) {
                window.clearTimeout(instance.localSymbols.parseTimeout);
            }

            instance.localSymbols.parseTimeout = window.setTimeout(function() {
                self.parseFile(editor, instance);
                instance.localSymbols.parseTimeout = null;
            }, self.parseDebounceMs);
        },

        parseFile: function(editor, instance) {
            var content = editor.getValue();
            var lines = content.split('\n');

            instance.localSymbols.classes = {};
            instance.localSymbols.functions = {};
            instance.localSymbols.variables = {};
            instance.localSymbols.imports = {};
            instance.localSymbols.occurrences = {};

            var currentClass = null;
            var currentClassIndent = -1;
            var currentFunction = null;
            var currentFunctionIndent = -1;

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];
                var lineNum = i + 1;
                var indent = this.getIndent(line);
                var trimmed = line.trim();

                if (!trimmed || trimmed.startsWith('#')) {
                    continue;
                }

                if (indent <= currentClassIndent) {
                    currentClass = null;
                    currentClassIndent = -1;
                }
                if (indent <= currentFunctionIndent) {
                    currentFunction = null;
                    currentFunctionIndent = -1;
                }

                var classMatch = trimmed.match(/^class\s+([A-Za-z_][A-Za-z0-9_]*)/);
                if (classMatch) {
                    var className = classMatch[1];
                    instance.localSymbols.classes[className] = {
                        name: className,
                        line: lineNum,
                        column: line.indexOf('class') + 6,
                        type: 'class'
                    };
                    currentClass = className;
                    currentClassIndent = indent;
                    continue;
                }

                var funcMatch = trimmed.match(/^(?:async\s+)?def\s+([A-Za-z_][A-Za-z0-9_]*)/);
                if (funcMatch) {
                    var funcName = funcMatch[1];
                    var funcInfo = {
                        name: funcName,
                        line: lineNum,
                        column: line.indexOf('def') + 4,
                        type: 'function',
                        parent: currentClass
                    };
                    if (currentClass) {
                        var key = currentClass + '.' + funcName;
                        instance.localSymbols.functions[key] = funcInfo;
                    }
                    instance.localSymbols.functions[funcName] = funcInfo;
                    currentFunction = funcName;
                    currentFunctionIndent = indent;
                    continue;
                }

                var importMatch = trimmed.match(/^from\s+([\w.]+)\s+import\s+(.+)$/);
                if (importMatch) {
                    var modulePath = importMatch[1];
                    var importedItems = importMatch[2];
                    var items = importedItems.split(',');
                    for (var j = 0; j < items.length; j++) {
                        var item = items[j].trim();
                        var asMatch = item.match(/^(\w+)\s+as\s+(\w+)$/);
                        if (asMatch) {
                            instance.localSymbols.imports[asMatch[2]] = {
                                name: asMatch[2],
                                originalName: asMatch[1],
                                module: modulePath,
                                line: lineNum,
                                column: line.indexOf(asMatch[2]),
                                type: 'import'
                            };
                        } else {
                            var cleanItem = item.replace(/[()]/g, '').trim();
                            if (cleanItem && /^\w+$/.test(cleanItem)) {
                                instance.localSymbols.imports[cleanItem] = {
                                    name: cleanItem,
                                    module: modulePath,
                                    line: lineNum,
                                    column: line.indexOf(cleanItem),
                                    type: 'import'
                                };
                            }
                        }
                    }
                    continue;
                }

                var simpleImportMatch = trimmed.match(/^import\s+([\w.]+)(?:\s+as\s+(\w+))?$/);
                if (simpleImportMatch) {
                    var modName = simpleImportMatch[2] || simpleImportMatch[1].split('.').pop();
                    instance.localSymbols.imports[modName] = {
                        name: modName,
                        module: simpleImportMatch[1],
                        line: lineNum,
                        column: line.indexOf(modName),
                        type: 'import'
                    };
                    continue;
                }

                if (indent === 0 && !currentFunction) {
                    var varMatch = trimmed.match(/^([A-Za-z_][A-Za-z0-9_]*)\s*=/);
                    if (varMatch) {
                        var varName = varMatch[1];
                        if (!instance.localSymbols.variables[varName]) {
                            instance.localSymbols.variables[varName] = {
                                name: varName,
                                line: lineNum,
                                column: line.indexOf(varName),
                                type: 'variable',
                                scope: 'module'
                            };
                        }
                    }
                }

                if (currentFunction) {
                    var localVarMatch = trimmed.match(/^([A-Za-z_][A-Za-z0-9_]*)\s*=/);
                    if (localVarMatch) {
                        var localVarName = localVarMatch[1];
                        var scopeKey = (currentClass ? currentClass + '.' : '') + currentFunction + '.' + localVarName;
                        if (!instance.localSymbols.variables[scopeKey]) {
                            instance.localSymbols.variables[scopeKey] = {
                                name: localVarName,
                                line: lineNum,
                                column: line.indexOf(localVarName),
                                type: 'variable',
                                scope: 'local',
                                function: currentFunction,
                                class: currentClass
                            };
                        }
                    }
                }
            }
        },

        getIndent: function(line) {
            var match = line.match(/^(\s*)/);
            return match ? match[1].length : 0;
        },

        findDefinition: function(instance, name, cursorLine) {
            var symbols = instance.localSymbols;

            if (symbols.classes[name]) {
                return symbols.classes[name];
            }

            if (symbols.functions[name]) {
                return symbols.functions[name];
            }

            if (symbols.imports[name]) {
                return symbols.imports[name];
            }

            if (symbols.variables[name]) {
                return symbols.variables[name];
            }

            var currentScope = this.findScopeAtLine(instance, cursorLine);
            if (currentScope) {
                var scopeKey = currentScope + '.' + name;
                if (symbols.variables[scopeKey]) {
                    return symbols.variables[scopeKey];
                }
            }

            return null;
        },

        findScopeAtLine: function(instance, line) {
            var symbols = instance.localSymbols;
            var bestMatch = null;
            var bestLine = 0;

            for (var funcName in symbols.functions) {
                var func = symbols.functions[funcName];
                if (func.line < line && func.line > bestLine) {
                    bestLine = func.line;
                    if (func.parent) {
                        bestMatch = func.parent + '.' + func.name;
                    } else {
                        bestMatch = func.name;
                    }
                }
            }

            return bestMatch;
        },

        findAllOccurrences: function(editor, instance, name, cursorLine) {
            var self = this;
            var content = editor.getValue();
            var lines = content.split('\n');
            var occurrences = [];

            var definition = self.findDefinition(instance, name, cursorLine);
            if (!definition) {
                return occurrences;
            }

            var defScope = null;
            if (definition.scope === 'local') {
                defScope = (definition.class ? definition.class + '.' : '') + definition.function;
            } else if (definition.scope === 'module') {
                defScope = 'module';
            } else if (definition.type === 'class' || definition.type === 'function' || definition.type === 'import') {
                defScope = 'module';
            }

            var currentClass = null;
            var currentClassIndent = -1;
            var currentFunction = null;
            var currentFunctionIndent = -1;

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];
                var lineNum = i + 1;
                var indent = self.getIndent(line);
                var trimmed = line.trim();

                var classMatch = trimmed.match(/^class\s+([A-Za-z_][A-Za-z0-9_]*)/);
                var funcMatch = trimmed.match(/^(?:async\s+)?def\s+([A-Za-z_][A-Za-z0-9_]*)/);

                if (trimmed && indent <= currentClassIndent && !classMatch) {
                    currentClass = null;
                    currentClassIndent = -1;
                }
                if (trimmed && indent <= currentFunctionIndent && !funcMatch) {
                    currentFunction = null;
                    currentFunctionIndent = -1;
                }

                if (classMatch) {
                    currentClass = classMatch[1];
                    currentClassIndent = indent;
                }

                if (funcMatch) {
                    currentFunction = funcMatch[1];
                    currentFunctionIndent = indent;
                }

                var lineScope = null;
                if (currentFunction) {
                    lineScope = (currentClass ? currentClass + '.' : '') + currentFunction;
                } else {
                    lineScope = 'module';
                }

                var isInScope = false;
                if (defScope === 'module') {
                    isInScope = true;
                } else if (defScope === lineScope) {
                    isInScope = true;
                }

                if (!isInScope) {
                    continue;
                }

                var regex = new RegExp('\\b' + name + '\\b', 'g');
                var match;
                while ((match = regex.exec(line)) !== null) {
                    var col = match.index;
                    var beforeChar = col > 0 ? line.charAt(col - 1) : '';
                    var afterChar = col + name.length < line.length ? line.charAt(col + name.length) : '';

                    if (beforeChar === '.' || beforeChar === '\'' || beforeChar === '"') {
                        continue;
                    }
                    if (afterChar === '(' && definition.type !== 'function' && definition.type !== 'class') {
                        continue;
                    }

                    occurrences.push({
                        line: lineNum,
                        column: col,
                        length: name.length
                    });
                }
            }

            return occurrences;
        }

    };

    window.ZatoIDELocalSymbols = ZatoIDELocalSymbols;

})();
