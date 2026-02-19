(function() {
    'use strict';

    var PythonExtractor = {

        extract: function(content) {
            console.log('[TRACE-SYMBOL] python.extract: starting, content.length=' + (content ? content.length : 0));
            var symbols = [];
            var lines = content.split('\n');
            console.log('[TRACE-SYMBOL] python.extract: split into ' + lines.length + ' lines');

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];
                var classMatch = line.match(/^class\s+(\w+)/);
                if (classMatch) {
                    var symbolLine = i + 1;
                    console.log('[TRACE-SYMBOL] python.extract: found class "' + classMatch[1] + '" at line ' + symbolLine + ' (0-indexed i=' + i + ')');
                    console.log('[TRACE-SYMBOL] python.extract: line content: "' + line.substring(0, 80) + '"');
                    symbols.push({
                        name: classMatch[1],
                        line: symbolLine,
                        type: 'class'
                    });
                }
            }

            console.log('[TRACE-SYMBOL] python.extract: returning ' + symbols.length + ' symbols');
            return symbols;
        }

    };

    if (window.ZatoIDESymbols) {
        ZatoIDESymbols.register('python', PythonExtractor);
    }

})();
