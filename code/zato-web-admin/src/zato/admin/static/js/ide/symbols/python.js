(function() {
    'use strict';

    var PythonExtractor = {

        extract: function(content) {
            var symbols = [];
            var lines = content.split('\n');

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];
                var classMatch = line.match(/^class\s+(\w+)/);
                if (classMatch) {
                    symbols.push({
                        name: classMatch[1],
                        line: i + 1,
                        type: 'class'
                    });
                }
            }

            return symbols;
        },

        extractMethods: function(content, classLine) {
            var methods = [];
            var lines = content.split('\n');

            var classStartIndex = classLine - 1;
            if (classStartIndex < 0 || classStartIndex >= lines.length) {
                return methods;
            }

            var classIndent = this.getIndent(lines[classStartIndex]);
            var methodIndent = -1;

            for (var i = classStartIndex + 1; i < lines.length; i++) {
                var line = lines[i];
                var trimmed = line.trim();

                if (trimmed === '') {
                    continue;
                }

                var currentIndent = this.getIndent(line);

                if (currentIndent <= classIndent && trimmed !== '') {
                    break;
                }

                var defMatch = line.match(/^(\s*)def\s+(\w+)\s*\(/);
                if (defMatch) {
                    var defIndent = defMatch[1].length;

                    if (methodIndent === -1) {
                        methodIndent = defIndent;
                    }

                    if (defIndent === methodIndent) {
                        methods.push({
                            name: defMatch[2],
                            line: i + 1,
                            type: 'method'
                        });
                    }
                }
            }

            return methods;
        },

        getIndent: function(line) {
            var match = line.match(/^(\s*)/);
            return match ? match[1].length : 0;
        }

    };

    if (window.ZatoIDESymbols) {
        ZatoIDESymbols.register('python', PythonExtractor);
    }

})();
