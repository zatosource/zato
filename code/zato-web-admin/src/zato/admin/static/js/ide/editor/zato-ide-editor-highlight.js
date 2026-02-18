(function() {
    'use strict';

    /**
     * ZatoIDEEditorHighlight - syntax highlighting for the editor.
     * Supports multiple languages with theme-aware token colors.
     * Stateless module - all highlighting is done via pure functions.
     */
    var ZatoIDEEditorHighlight = {

        /**
         * Token patterns for each language.
         * Order matters - patterns are applied in sequence.
         */
        patterns: {
            python: [
                { type: 'comment', regex: /#.*$/gm },
                { type: 'string', regex: /"""[\s\S]*?"""|'''[\s\S]*?'''|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'/g },
                { type: 'keyword', regex: /\b(and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield|True|False|None)\b/g },
                { type: 'builtin', regex: /\b(print|len|range|str|int|float|list|dict|set|tuple|open|input|type|isinstance|hasattr|getattr|setattr|super|property|staticmethod|classmethod)\b/g },
                { type: 'decorator', regex: /@[\w.]+/g },
                { type: 'number', regex: /\b\d+\.?\d*([eE][+-]?\d+)?\b/g },
                { type: 'function', regex: /\b([a-zA-Z_]\w*)\s*(?=\()/g },
                { type: 'class-name', regex: /\bclass\s+([A-Z]\w*)/g }
            ],
            sql: [
                { type: 'comment', regex: /--.*$/gm },
                { type: 'comment', regex: /\/\*[\s\S]*?\*\//g },
                { type: 'string', regex: /'(?:[^'\\]|\\.)*'/g },
                { type: 'keyword', regex: /\b(SELECT|FROM|WHERE|AND|OR|NOT|IN|IS|NULL|AS|ON|JOIN|LEFT|RIGHT|INNER|OUTER|FULL|CROSS|ORDER|BY|GROUP|HAVING|LIMIT|OFFSET|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|INDEX|VIEW|DROP|ALTER|ADD|COLUMN|PRIMARY|KEY|FOREIGN|REFERENCES|UNIQUE|DEFAULT|CHECK|CONSTRAINT|CASCADE|UNION|ALL|DISTINCT|CASE|WHEN|THEN|ELSE|END|EXISTS|BETWEEN|LIKE|ILIKE|ASC|DESC|NULLS|FIRST|LAST|WITH|RECURSIVE|RETURNING|TRUNCATE|BEGIN|COMMIT|ROLLBACK|TRANSACTION)\b/gi },
                { type: 'function', regex: /\b(COUNT|SUM|AVG|MIN|MAX|COALESCE|NULLIF|CAST|CONVERT|SUBSTRING|TRIM|UPPER|LOWER|LENGTH|CONCAT|NOW|CURRENT_DATE|CURRENT_TIME|CURRENT_TIMESTAMP|EXTRACT|DATE_PART|TO_CHAR|TO_DATE|TO_NUMBER)\b/gi },
                { type: 'number', regex: /\b\d+\.?\d*\b/g },
                { type: 'operator', regex: /[=<>!]+|::/g }
            ],
            yaml: [
                { type: 'comment', regex: /#.*$/gm },
                { type: 'string', regex: /"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'/g },
                { type: 'key', regex: /^[\s]*[\w.-]+(?=\s*:)/gm },
                { type: 'keyword', regex: /\b(true|false|null|yes|no|on|off)\b/gi },
                { type: 'number', regex: /\b\d+\.?\d*\b/g },
                { type: 'anchor', regex: /[&*][\w-]+/g },
                { type: 'tag', regex: /![\w!.-]+/g }
            ],
            json: [
                { type: 'string', regex: /"(?:[^"\\]|\\.)*"/g },
                { type: 'keyword', regex: /\b(true|false|null)\b/g },
                { type: 'number', regex: /-?\b\d+\.?\d*([eE][+-]?\d+)?\b/g },
                { type: 'property', regex: /"[\w-]+"(?=\s*:)/g }
            ],
            ini: [
                { type: 'comment', regex: /[;#].*$/gm },
                { type: 'section', regex: /^\s*\[[\w.-]+\]/gm },
                { type: 'key', regex: /^[\s]*[\w.-]+(?=\s*=)/gm },
                { type: 'string', regex: /"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'/g },
                { type: 'number', regex: /\b\d+\.?\d*\b/g },
                { type: 'keyword', regex: /\b(true|false|yes|no|on|off)\b/gi }
            ],
            xml: [
                { type: 'comment', regex: /<!--[\s\S]*?-->/g },
                { type: 'cdata', regex: /<!\[CDATA\[[\s\S]*?\]\]>/g },
                { type: 'doctype', regex: /<!DOCTYPE[^>]*>/gi },
                { type: 'tag', regex: /<\/?[\w:-]+/g },
                { type: 'tag-close', regex: /\/?>/g },
                { type: 'attribute', regex: /[\w:-]+(?=\s*=)/g },
                { type: 'string', regex: /"[^"]*"|'[^']*'/g }
            ],
            html: [
                { type: 'comment', regex: /<!--[\s\S]*?-->/g },
                { type: 'doctype', regex: /<!DOCTYPE[^>]*>/gi },
                { type: 'tag', regex: /<\/?[\w-]+/g },
                { type: 'tag-close', regex: /\/?>/g },
                { type: 'attribute', regex: /[\w-]+(?=\s*=)/g },
                { type: 'string', regex: /"[^"]*"|'[^']*'/g }
            ],
            css: [
                { type: 'comment', regex: /\/\*[\s\S]*?\*\//g },
                { type: 'selector', regex: /[.#]?[\w-]+(?=\s*[,{])/g },
                { type: 'property', regex: /[\w-]+(?=\s*:)/g },
                { type: 'string', regex: /"[^"]*"|'[^']*'/g },
                { type: 'number', regex: /-?\d+\.?\d*(px|em|rem|%|vh|vw|deg|s|ms)?/g },
                { type: 'color', regex: /#[0-9a-fA-F]{3,8}\b/g },
                { type: 'keyword', regex: /\b(important|inherit|initial|unset|none|auto)\b/gi },
                { type: 'function', regex: /[\w-]+(?=\()/g }
            ],
            javascript: [
                { type: 'comment', regex: /\/\/.*$/gm },
                { type: 'comment', regex: /\/\*[\s\S]*?\*\//g },
                { type: 'string', regex: /`(?:[^`\\]|\\.)*`|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'/g },
                { type: 'keyword', regex: /\b(break|case|catch|class|const|continue|debugger|default|delete|do|else|export|extends|finally|for|function|if|import|in|instanceof|let|new|return|super|switch|this|throw|try|typeof|var|void|while|with|yield|async|await|of)\b/g },
                { type: 'builtin', regex: /\b(Array|Boolean|Date|Error|Function|JSON|Math|Number|Object|Promise|RegExp|String|Symbol|console|document|window|undefined|null|true|false|NaN|Infinity)\b/g },
                { type: 'number', regex: /\b\d+\.?\d*([eE][+-]?\d+)?\b/g },
                { type: 'function', regex: /\b([a-zA-Z_$][\w$]*)\s*(?=\()/g },
                { type: 'operator', regex: /[=!<>]=?|[+\-*/%]|&&|\|\||\?\?/g }
            ],
            text: []
        },

        /**
         * Highlights code and returns HTML string.
         */
        highlight: function(code, language) {
            if (!code) {
                return '<div class="zato-ide-editor-line"></div>';
            }

            var lang = language || 'text';
            var patterns = this.patterns[lang] || this.patterns.text;

            if (patterns.length === 0) {
                return this.wrapLines(this.escapeHtml(code));
            }

            var tokens = this.tokenize(code, patterns);
            var html = this.renderTokens(code, tokens);
            return this.wrapLines(html);
        },

        /**
         * Tokenizes code using the given patterns.
         */
        tokenize: function(code, patterns) {
            var tokens = [];
            var covered = new Array(code.length);

            for (var i = 0; i < patterns.length; i++) {
                var pattern = patterns[i];
                var regex = new RegExp(pattern.regex.source, pattern.regex.flags);
                var match;

                while ((match = regex.exec(code)) !== null) {
                    var start = match.index;
                    var end = start + match[0].length;
                    var overlap = false;

                    for (var j = start; j < end; j++) {
                        if (covered[j]) {
                            overlap = true;
                            break;
                        }
                    }

                    if (!overlap) {
                        tokens.push({
                            type: pattern.type,
                            start: start,
                            end: end,
                            text: match[0]
                        });

                        for (var k = start; k < end; k++) {
                            covered[k] = true;
                        }
                    }
                }
            }

            tokens.sort(function(a, b) {
                return a.start - b.start;
            });

            return tokens;
        },

        /**
         * Renders tokens to HTML.
         */
        renderTokens: function(code, tokens) {
            var result = '';
            var pos = 0;

            for (var i = 0; i < tokens.length; i++) {
                var token = tokens[i];

                if (token.start > pos) {
                    result += this.escapeHtml(code.substring(pos, token.start));
                }

                result += '<span class="zato-ide-token-' + token.type + '">';
                result += this.escapeHtml(token.text);
                result += '</span>';

                pos = token.end;
            }

            if (pos < code.length) {
                result += this.escapeHtml(code.substring(pos));
            }

            return result;
        },

        /**
         * Wraps code in line divs for proper display.
         */
        wrapLines: function(html) {
            var lines = html.split('\n');
            var result = '';

            for (var i = 0; i < lines.length; i++) {
                var lineContent = lines[i] || '';
                result += '<div class="zato-ide-editor-line">' + lineContent + '</div>';
            }

            return result;
        },

        /**
         * Escapes HTML entities.
         */
        escapeHtml: function(text) {
            return text
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');
        },

        /**
         * Detects language from file extension.
         */
        detectLanguage: function(filename) {
            if (!filename) {
                return 'text';
            }

            var ext = filename.split('.').pop().toLowerCase();
            var map = {
                'py': 'python',
                'sql': 'sql',
                'yaml': 'yaml',
                'yml': 'yaml',
                'json': 'json',
                'ini': 'ini',
                'cfg': 'ini',
                'conf': 'ini',
                'xml': 'xml',
                'html': 'html',
                'htm': 'html',
                'css': 'css',
                'js': 'javascript',
                'mjs': 'javascript',
                'txt': 'text',
                'md': 'text',
                'log': 'text'
            };

            return map[ext] || 'text';
        }
    };

    window.ZatoIDEEditorHighlight = ZatoIDEEditorHighlight;

})();
