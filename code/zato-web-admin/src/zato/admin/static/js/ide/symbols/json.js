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
        }

    };

    if (window.ZatoIDESymbols) {
        ZatoIDESymbols.register('json', JSONExtractor);
    }

})();
