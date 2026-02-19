(function() {
    'use strict';

    var SQLExtractor = {

        extract: function(content) {
            var symbols = [];
            var lines = content.split('\n');

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];

                var createMatch = line.match(/^\s*CREATE\s+(TABLE|VIEW|PROCEDURE|FUNCTION|INDEX|TRIGGER)\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)/i);
                if (createMatch) {
                    symbols.push({
                        name: createMatch[2],
                        line: i + 1,
                        type: createMatch[1].toLowerCase()
                    });
                    continue;
                }

                var sectionMatch = line.match(/^--\s*##\s*(.+)$/);
                if (sectionMatch) {
                    symbols.push({
                        name: sectionMatch[1].trim(),
                        line: i + 1,
                        type: 'section'
                    });
                }
            }

            return symbols;
        }

    };

    if (window.ZatoIDESymbols) {
        ZatoIDESymbols.register('sql', SQLExtractor);
    }

})();
