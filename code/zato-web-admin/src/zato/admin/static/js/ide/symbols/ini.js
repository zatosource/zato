(function() {
    'use strict';

    var INIExtractor = {

        extract: function(content) {
            console.log('[TRACE-SYMBOL] ini.extract: starting, content.length=' + (content ? content.length : 0));
            var symbols = [];
            var lines = content.split('\n');
            console.log('[TRACE-SYMBOL] ini.extract: split into ' + lines.length + ' lines');

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];

                var sectionMatch = line.match(/^\[([^\]]+)\]/);
                if (sectionMatch) {
                    var symbolLine = i + 1;
                    console.log('[TRACE-SYMBOL] ini.extract: found section "' + sectionMatch[1] + '" at line ' + symbolLine + ' (0-indexed i=' + i + ')');
                    symbols.push({
                        name: sectionMatch[1],
                        line: symbolLine,
                        type: 'section'
                    });
                }
            }

            console.log('[TRACE-SYMBOL] ini.extract: returning ' + symbols.length + ' symbols');
            return symbols;
        },

        extractMethods: function(content, sectionLine) {
            var methods = [];
            var lines = content.split('\n');

            var sectionStartIndex = sectionLine - 1;
            if (sectionStartIndex < 0 || sectionStartIndex >= lines.length) {
                return methods;
            }

            for (var i = sectionStartIndex + 1; i < lines.length; i++) {
                var line = lines[i];
                var trimmed = line.trim();

                if (trimmed === '' || trimmed.match(/^[;#]/)) {
                    continue;
                }

                if (line.match(/^\[([^\]]+)\]/)) {
                    break;
                }

                var keyMatch = line.match(/^(\w[\w\-]*)\s*=/);
                if (keyMatch) {
                    methods.push({
                        name: keyMatch[1],
                        line: i + 1,
                        type: 'setting'
                    });
                }
            }

            return methods;
        }

    };

    if (window.ZatoIDESymbols) {
        ZatoIDESymbols.register('ini', INIExtractor);
    }

})();
