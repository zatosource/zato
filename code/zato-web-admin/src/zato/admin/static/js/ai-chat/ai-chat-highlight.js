(function() {
    'use strict';

    var AIChatHighlight = {

        cssLoaded: false,
        cssVersion: 2,
        cache: {},

        init: function() {
            this.loadCSS();
        },

        loadCSS: function() {
            if (this.cssLoaded) {
                return;
            }

            var self = this;

            fetch('/zato/ai-chat/highlight/css/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            }).then(function(response) {
                return response.json();
            }).then(function(data) {
                if (data.css) {
                    var style = document.createElement('style');
                    style.textContent = data.css;
                    document.head.appendChild(style);
                    self.cssLoaded = true;
                }
            }).catch(function(error) {
                console.error('AIChatHighlight.loadCSS error:', error);
            });
        },

        highlightCodeBlocks: function(container) {
            if (!container) {
                return;
            }

            var self = this;
            var codeBlocks = container.querySelectorAll('pre code');

            for (var i = 0; i < codeBlocks.length; i++) {
                var codeEl = codeBlocks[i];

                if (codeEl.classList.contains('highlighted')) {
                    continue;
                }

                var language = this.getLanguageFromClass(codeEl);
                var code = codeEl.textContent;

                if (!code.trim()) {
                    continue;
                }

                var cacheKey = language + ':' + code;
                if (this.cache[cacheKey]) {
                    codeEl.innerHTML = this.cache[cacheKey];
                    codeEl.classList.add('highlighted');
                    continue;
                }

                this.highlightCode(codeEl, code, language);
            }
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
        },

        highlightCode: function(codeEl, code, language) {
            var self = this;

            fetch('/zato/ai-chat/highlight/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    code: code,
                    language: language
                })
            }).then(function(response) {
                return response.json();
            }).then(function(data) {
                if (data.html) {
                    var cacheKey = language + ':' + code;
                    self.cache[cacheKey] = data.html;
                    codeEl.innerHTML = data.html;
                    codeEl.classList.add('highlighted');
                }
            }).catch(function(error) {
                console.error('AIChatHighlight.highlightCode error:', error);
            });
        },

        getCsrfToken: function() {
            var cookieValue = null;
            var name = 'csrftoken';
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    };

    AIChatHighlight.init();

    window.AIChatHighlight = AIChatHighlight;

})();
