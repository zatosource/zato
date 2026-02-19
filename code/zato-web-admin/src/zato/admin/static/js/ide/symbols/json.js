(function() {
    'use strict';

    var JSONExtractor = {

        extract: function(content) {
            console.log('[TRACE-SYMBOL] json.extract: starting, content.length=' + (content ? content.length : 0));
            var symbols = [];
            var lines = content.split('\n');
            console.log('[TRACE-SYMBOL] json.extract: split into ' + lines.length + ' lines');

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];

                var keyMatch = line.match(/^\s{0,2}"(\w+)"\s*:/);
                if (keyMatch) {
                    var symbolLine = i + 1;
                    console.log('[TRACE-SYMBOL] json.extract: found key "' + keyMatch[1] + '" at line ' + symbolLine + ' (0-indexed i=' + i + ')');
                    symbols.push({
                        name: keyMatch[1],
                        line: symbolLine,
                        type: 'key'
                    });
                }
            }

            console.log('[TRACE-SYMBOL] json.extract: returning ' + symbols.length + ' symbols');
            return symbols;
        },

        extractMethods: function(content, keyLine) {
            var methods = [];
            var lines = content.split('\n');

            var keyStartIndex = keyLine - 1;
            if (keyStartIndex < 0 || keyStartIndex >= lines.length) {
                return methods;
            }

            var braceDepth = 0;
            var started = false;

            for (var i = keyStartIndex; i < lines.length; i++) {
                var line = lines[i];

                for (var j = 0; j < line.length; j++) {
                    var ch = line[j];
                    if (ch === '{' || ch === '[') {
                        if (started) {
                            braceDepth++;
                        }
                        started = true;
                    } else if (ch === '}' || ch === ']') {
                        braceDepth--;
                        if (braceDepth < 0) {
                            return methods;
                        }
                    }
                }

                if (i === keyStartIndex) {
                    continue;
                }

                if (braceDepth === 1) {
                    var nestedMatch = line.match(/^\s{4}"(\w+)"\s*:/);
                    if (nestedMatch) {
                        methods.push({
                            name: nestedMatch[1],
                            line: i + 1,
                            type: 'key'
                        });
                    }
                }
            }

            return methods;
        }

    };

    if (window.ZatoIDESymbols) {
        ZatoIDESymbols.register('json', JSONExtractor);
    }

})();
