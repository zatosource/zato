(function() {
    'use strict';

    var ZatoIDESymbols = {

        extractors: {},

        register: function(language, extractor) {
            this.extractors[language] = extractor;
        },

        extract: function(content, language) {
            var extractor = this.extractors[language];
            if (!extractor) {
                return [];
            }
            return extractor.extract(content);
        },

        getExtractor: function(language) {
            return this.extractors[language] || null;
        }

    };

    window.ZatoIDESymbols = ZatoIDESymbols;

})();
