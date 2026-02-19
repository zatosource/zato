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
        }

    };

    if (window.ZatoIDESymbols) {
        ZatoIDESymbols.register('ini', INIExtractor);
    }

})();
