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
        }

    };

    if (window.ZatoIDESymbols) {
        ZatoIDESymbols.register('python', PythonExtractor);
    }

})();
