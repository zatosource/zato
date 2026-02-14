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
            html = this.renderBold(html);
            html = this.renderItalic(html);
            html = this.renderLinks(html);
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
            return html.replace(pattern, function(match, lang, code) {
                var langClass = lang ? ' class="language-' + lang + '"' : '';
                return '<pre><code' + langClass + '>' + code.trim() + '</code></pre>';
            });
        },

        renderInlineCode: function(html) {
            return html.replace(/`([^`]+)`/g, '<code>$1</code>');
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

        renderLinks: function(html) {
            return html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
        },

        renderLists: function(html) {
            var lines = html.split('\n');
            var out = [];
            var inList = false;
            var listType = null;

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];
                var ulMatch = line.match(/^(\s*)[-*]\s+(.+)$/);
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
            return html.replace(/\n/g, '<br>');
        }
    };

    window.AIChatMarkdown = AIChatMarkdown;

})();
