(function() {
    'use strict';

    var INIExtractor = {

        extract: function(content) {
            var symbols = [];
            var lines = content.split('\n');

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];

                var sectionMatch = line.match(/^\[([^\]]+)\]/);
                if (sectionMatch) {
                    symbols.push({
                        name: sectionMatch[1],
                        line: i + 1,
                        type: 'section'
                    });
                }
            }

            return symbols;
        }

    };

    if (window.ZatoIDESymbols) {
        ZatoIDESymbols.register('ini', INIExtractor);
    }

})();
