(function() {
    'use strict';

    var JSONExtractor = {

        extract: function(content) {
            var symbols = [];
            var lines = content.split('\n');

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];

                var keyMatch = line.match(/^\s{0,2}"(\w+)"\s*:/);
                if (keyMatch) {
                    symbols.push({
                        name: keyMatch[1],
                        line: i + 1,
                        type: 'key'
                    });
                }
            }

            return symbols;
        }

    };

    if (window.ZatoIDESymbols) {
        ZatoIDESymbols.register('json', JSONExtractor);
    }

})();
