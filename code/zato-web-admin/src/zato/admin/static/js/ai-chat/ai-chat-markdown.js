(function() {
    'use strict';

    var AIChatMarkdown = {

        render: function(text) {
            if (!text) {
                return '';
            }

            var html = this.escapeHtml(text);

            html = this.renderCodeBlocks(html);
            html = this.renderInlineCode(html);
            html = this.renderTables(html);
            html = this.renderBlockquotes(html);
            html = this.renderHeaders(html);
            html = this.renderHorizontalRules(html);
            html = this.renderStrikethrough(html);
            html = this.renderBoldItalic(html);
            html = this.renderBold(html);
            html = this.renderItalic(html);
            html = this.renderImages(html);
            html = this.renderLinks(html);
            html = this.renderCheckboxes(html);
            html = this.renderLists(html);
            html = this.renderLineBreaks(html);

            return html;
        },

        escapeHtml: function(text) {
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        renderCodeBlocks: function(html) {
            var pattern = /```(\w*)\n([\s\S]*?)```/g;
            html = html.replace(pattern, function(match, lang, code) {
                var langClass = lang ? ' class="language-' + lang + '"' : '';
                return '<pre><code' + langClass + '>' + code.trim() + '</code></pre>';
            });

            var indentedPattern = /(?:^|\n)((?:    .+\n?)+)/g;
            html = html.replace(indentedPattern, function(match, code) {
                var cleanCode = code.replace(/^    /gm, '');
                return '\n<pre><code>' + cleanCode.trim() + '</code></pre>\n';
            });

            return html;
        },

        renderInlineCode: function(html) {
            return html.replace(/`([^`]+)`/g, '<code>$1</code>');
        },

        renderHeaders: function(html) {
            html = html.replace(/^###### (.+)$/gm, '<h6>$1</h6>');
            html = html.replace(/^##### (.+)$/gm, '<h5>$1</h5>');
            html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
            html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
            html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
            html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
            return html;
        },

        renderBlockquotes: function(html) {
            var lines = html.split('\n');
            var out = [];
            var quoteDepth = 0;

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];
                var match = line.match(/^(>+)\s*(.*)$/);

                if (match) {
                    var depth = match[1].length;
                    var content = match[2];

                    while (quoteDepth < depth) {
                        out.push('<blockquote>');
                        quoteDepth++;
                    }
                    while (quoteDepth > depth) {
                        out.push('</blockquote>');
                        quoteDepth--;
                    }
                    out.push(content);
                } else {
                    while (quoteDepth > 0) {
                        out.push('</blockquote>');
                        quoteDepth--;
                    }
                    out.push(line);
                }
            }

            while (quoteDepth > 0) {
                out.push('</blockquote>');
                quoteDepth--;
            }

            return out.join('\n');
        },

        renderHorizontalRules: function(html) {
            return html.replace(/^(-{3,}|\*{3,}|_{3,})$/gm, '<hr>');
        },

        renderStrikethrough: function(html) {
            return html.replace(/~~([^~]+)~~/g, '<del>$1</del>');
        },

        renderBoldItalic: function(html) {
            html = html.replace(/\*\*\*([^*]+)\*\*\*/g, '<strong><em>$1</em></strong>');
            html = html.replace(/___([^_]+)___/g, '<strong><em>$1</em></strong>');
            return html;
        },

        renderBold: function(html) {
            html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
            html = html.replace(/__([^_]+)__/g, '<strong>$1</strong>');
            return html;
        },

        renderItalic: function(html) {
            html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
            html = html.replace(/_([^_]+)_/g, '<em>$1</em>');
            return html;
        },

        renderImages: function(html) {
            return html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">');
        },

        renderLinks: function(html) {
            return html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
        },

        renderCheckboxes: function(html) {
            html = html.replace(/\[x\]/gi, '<input type="checkbox" checked disabled>');
            html = html.replace(/\[ \]/g, '<input type="checkbox" disabled>');
            return html;
        },

        renderTables: function(html) {
            var lines = html.split('\n');
            var out = [];
            var inTable = false;
            var tableRows = [];

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i].trim();

                if (line.match(/^\|.*\|$/)) {
                    if (line.match(/^\|[\s\-:|]+\|$/)) {
                        continue;
                    }
                    tableRows.push(line);
                    inTable = true;
                } else {
                    if (inTable && tableRows.length > 0) {
                        out.push(this.buildTable(tableRows));
                        tableRows = [];
                        inTable = false;
                    }
                    out.push(line);
                }
            }

            if (tableRows.length > 0) {
                out.push(this.buildTable(tableRows));
            }

            return out.join('\n');
        },

        buildTable: function(rows) {
            var html = '<table class="ai-chat-table">';

            for (var i = 0; i < rows.length; i++) {
                var cells = rows[i].split('|').filter(function(c) {
                    return c.trim() !== '';
                });

                var tag = (i === 0) ? 'th' : 'td';
                html += '<tr>';
                for (var j = 0; j < cells.length; j++) {
                    html += '<' + tag + '>' + cells[j].trim() + '</' + tag + '>';
                }
                html += '</tr>';
            }

            html += '</table>';
            return html;
        },

        renderLists: function(html) {
            var lines = html.split('\n');
            var out = [];
            var inList = false;
            var listType = null;

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];
                var ulMatch = line.match(/^(\s*)[-*+]\s+(.+)$/);
                var olMatch = line.match(/^(\s*)\d+\.\s+(.+)$/);

                if (ulMatch) {
                    if (!inList || listType !== 'ul') {
                        if (inList) {
                            out.push('</' + listType + '>');
                        }
                        out.push('<ul>');
                        inList = true;
                        listType = 'ul';
                    }
                    out.push('<li>' + ulMatch[2] + '</li>');
                } else if (olMatch) {
                    if (!inList || listType !== 'ol') {
                        if (inList) {
                            out.push('</' + listType + '>');
                        }
                        out.push('<ol>');
                        inList = true;
                        listType = 'ol';
                    }
                    out.push('<li>' + olMatch[2] + '</li>');
                } else {
                    if (inList) {
                        out.push('</' + listType + '>');
                        inList = false;
                        listType = null;
                    }
                    out.push(line);
                }
            }

            if (inList) {
                out.push('</' + listType + '>');
            }

            return out.join('\n');
        },

        renderLineBreaks: function(html) {
            html = html.replace(/<\/h([1-6])>\n/g, '</h$1>');
            html = html.replace(/<\/blockquote>\n/g, '</blockquote>');
            html = html.replace(/<\/li>\n/g, '</li>');
            html = html.replace(/<\/ul>\n/g, '</ul>');
            html = html.replace(/<\/ol>\n/g, '</ol>');
            html = html.replace(/<\/table>\n/g, '</table>');
            html = html.replace(/<\/pre>\n/g, '</pre>');
            html = html.replace(/<hr>\n/g, '<hr>');
            html = html.replace(/\n/g, '<br>');
            return html;
        }
    };

    window.AIChatMarkdown = AIChatMarkdown;

})();
