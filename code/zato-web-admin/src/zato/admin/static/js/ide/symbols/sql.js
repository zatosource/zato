(function() {
    'use strict';

    var SQLExtractor = {

        extract: function(content) {
            console.log('[TRACE-SYMBOL] sql.extract: starting, content.length=' + (content ? content.length : 0));
            var symbols = [];
            var lines = content.split('\n');
            console.log('[TRACE-SYMBOL] sql.extract: split into ' + lines.length + ' lines');

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];

                var createMatch = line.match(/^\s*CREATE\s+(TABLE|VIEW|PROCEDURE|FUNCTION|INDEX|TRIGGER)\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)/i);
                if (createMatch) {
                    var symbolLine = i + 1;
                    console.log('[TRACE-SYMBOL] sql.extract: found CREATE "' + createMatch[2] + '" at line ' + symbolLine + ' (0-indexed i=' + i + ')');
                    symbols.push({
                        name: createMatch[2],
                        line: symbolLine,
                        type: createMatch[1].toLowerCase()
                    });
                    continue;
                }

                var sectionMatch = line.match(/^--\s*##\s*(.+)$/);
                if (sectionMatch) {
                    var sectionLine = i + 1;
                    console.log('[TRACE-SYMBOL] sql.extract: found section "' + sectionMatch[1].trim() + '" at line ' + sectionLine + ' (0-indexed i=' + i + ')');
                    symbols.push({
                        name: sectionMatch[1].trim(),
                        line: sectionLine,
                        type: 'section'
                    });
                }
            }

            console.log('[TRACE-SYMBOL] sql.extract: returning ' + symbols.length + ' symbols');
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

                if (trimmed === '') {
                    continue;
                }

                if (line.match(/^--\s*##\s*.+$/)) {
                    break;
                }

                var createMatch = line.match(/^\s*CREATE\s+(TABLE|VIEW|PROCEDURE|FUNCTION|INDEX|TRIGGER)\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)/i);
                if (createMatch) {
                    methods.push({
                        name: createMatch[2],
                        line: i + 1,
                        type: createMatch[1].toLowerCase()
                    });
                    continue;
                }

                var selectMatch = line.match(/^\s*(SELECT|INSERT|UPDATE|DELETE)\s+/i);
                if (selectMatch) {
                    var stmtType = selectMatch[1].toUpperCase();
                    methods.push({
                        name: stmtType + ' (line ' + (i + 1) + ')',
                        line: i + 1,
                        type: 'statement'
                    });
                }
            }

            return methods;
        }

    };

    if (window.ZatoIDESymbols) {
        ZatoIDESymbols.register('sql', SQLExtractor);
    }

})();
