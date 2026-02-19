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

        extractMethods: function(content, language, classLine) {
            var extractor = this.extractors[language];
            if (!extractor || typeof extractor.extractMethods !== 'function') {
                return [];
            }
            return extractor.extractMethods(content, classLine);
        },

        getExtractor: function(language) {
            return this.extractors[language] || null;
        },

        findSymbolAtLine: function(content, language, line) {
            var extractor = this.extractors[language];
            if (!extractor) {
                return null;
            }
            var symbols = extractor.extract(content);
            if (symbols.length === 0) {
                return null;
            }

            var found = null;
            for (var i = 0; i < symbols.length; i++) {
                if (symbols[i].line <= line) {
                    found = symbols[i];
                } else {
                    break;
                }
            }
            return found;
        },

        findMethodAtLine: function(content, language, symbolLine, line) {
            var extractor = this.extractors[language];
            if (!extractor || typeof extractor.extractMethods !== 'function') {
                return null;
            }
            var methods = extractor.extractMethods(content, symbolLine);
            if (methods.length === 0) {
                return null;
            }

            var found = null;
            for (var i = 0; i < methods.length; i++) {
                if (methods[i].line <= line) {
                    found = methods[i];
                } else {
                    break;
                }
            }
            return found;
        }

    };

    window.ZatoIDESymbols = ZatoIDESymbols;

})();
