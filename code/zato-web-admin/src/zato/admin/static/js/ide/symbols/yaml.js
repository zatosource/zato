(function() {
    'use strict';

    var YAMLExtractor = {

        extract: function(content) {
            console.log('[TRACE-SYMBOL] yaml.extract: starting, content.length=' + (content ? content.length : 0));
            var symbols = [];
            var lines = content.split('\n');
            console.log('[TRACE-SYMBOL] yaml.extract: split into ' + lines.length + ' lines');

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];

                if (line.match(/^#/)) {
                    continue;
                }

                var keyMatch = line.match(/^(\w[\w\-]*)\s*:/);
                if (keyMatch) {
                    var symbolLine = i + 1;
                    console.log('[TRACE-SYMBOL] yaml.extract: found key "' + keyMatch[1] + '" at line ' + symbolLine + ' (0-indexed i=' + i + ')');
                    symbols.push({
                        name: keyMatch[1],
                        line: symbolLine,
                        type: 'key'
                    });
                }
            }

            console.log('[TRACE-SYMBOL] yaml.extract: returning ' + symbols.length + ' symbols');
            return symbols;
        }

    };

    if (window.ZatoIDESymbols) {
        ZatoIDESymbols.register('yaml', YAMLExtractor);
    }

})();
