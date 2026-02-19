(function() {
    'use strict';

    var YAMLExtractor = {

        extract: function(content) {
            var symbols = [];
            var lines = content.split('\n');

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];

                if (line.match(/^#/)) {
                    continue;
                }

                var keyMatch = line.match(/^(\w[\w\-]*)\s*:/);
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
        ZatoIDESymbols.register('yaml', YAMLExtractor);
    }

})();
