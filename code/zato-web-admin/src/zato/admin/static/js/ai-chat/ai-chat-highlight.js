(function() {
    'use strict';

    var AIChatHighlight = {

        hljsLoaded: false,
        hljsLoading: false,

        init: function() {
            this.loadHighlightJs();
        },

        loadHighlightJs: function() {
            if (this.hljsLoaded || this.hljsLoading) {
                return;
            }
            this.hljsLoading = true;

            var self = this;

            var link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = '/static/css/ai-chat/hljs-atom-one-dark.css';
            document.head.appendChild(link);

            var script = document.createElement('script');
            script.src = '/static/js/ai-chat/hljs.min.js';
            script.onload = function() {
                self.hljsLoaded = true;
                self.hljsLoading = false;
            };
            script.onerror = function() {
                self.hljsLoading = false;
                console.error('Failed to load highlight.js');
            };
            document.head.appendChild(script);
        },

        highlightCodeBlocks: function(container) {
            if (!container) {
                return;
            }

            var codeBlocks = container.querySelectorAll('pre code');
            for (var i = 0; i < codeBlocks.length; i++) {
                this.processCodeElement(codeBlocks[i]);
            }
        },

        processCodeElement: function(codeEl) {
            if (codeEl.classList.contains('hljs')) {
                return;
            }

            if (!this.hljsLoaded || typeof hljs === 'undefined') {
                return;
            }

            hljs.highlightElement(codeEl);
        },

        getLanguageFromClass: function(codeEl) {
            var classes = codeEl.className.split(' ');
            for (var i = 0; i < classes.length; i++) {
                var cls = classes[i];
                if (cls.startsWith('language-')) {
                    return cls.substring(9);
                }
            }
            return '';
        }
    };

    AIChatHighlight.init();

    window.AIChatHighlight = AIChatHighlight;

})();
