(function() {
    'use strict';

    var AIChatAttachments = {

        fileIconMap: {
            'application/json': 'JSON-1.svg',
            'application/javascript': 'JSX.svg',
            'text/javascript': 'JSX.svg',
            'application/pdf': 'Adobe-Acrobat.svg',
            'text/html': 'DOM.svg',
            'text/xml': 'Default.svg',
            'application/xml': 'Default.svg',
            'text/css': 'Stylus.svg',
            'text/plain': 'Default.svg',
            'text/markdown': 'MarkdownLint.svg',
            'text/x-python': 'Python.svg',
            'application/x-python': 'Python.svg',
            'text/x-java': 'Default.svg',
            'text/x-c': 'Default.svg',
            'text/x-c++': 'C++.svg',
            'text/x-ruby': 'RubyGems.svg',
            'text/x-go': 'Go.svg',
            'text/x-rust': 'Default.svg',
            'text/x-typescript': 'TypeScript.svg',
            'text/x-sql': 'SQLite.svg',
            'text/x-yaml': 'YAML.svg',
            'text/yaml': 'YAML.svg',
            'application/x-yaml': 'YAML.svg',
            'text/x-sh': 'Terminal.svg',
            'application/x-sh': 'Terminal.svg',
            'image/png': 'Image.svg',
            'image/jpeg': 'Image.svg',
            'image/gif': 'Image.svg',
            'image/svg+xml': 'Default.svg',
            'image/webp': 'Image.svg',
            'application/zip': 'Brotli.svg',
            'application/x-tar': 'Brotli.svg',
            'application/gzip': 'Brotli.svg',
            'application/x-rar-compressed': 'Brotli.svg',
            'video/mp4': 'Video.svg',
            'video/webm': 'Video.svg',
            'audio/mpeg': 'Audacity.svg',
            'audio/wav': 'Audacity.svg',
            'application/msword': 'Microsoft-Word.svg',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Microsoft-Word.svg',
            'application/vnd.ms-excel': 'Microsoft-Excel.svg',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Microsoft-Excel.svg',
            'application/vnd.ms-powerpoint': 'Microsoft-PowerPoint.svg',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'Microsoft-PowerPoint.svg'
        },

        extensionIconMap: {
            'js': 'JSX.svg',
            'jsx': 'JSX.svg',
            'ts': 'TypeScript.svg',
            'tsx': 'TSX.svg',
            'json': 'JSON-1.svg',
            'py': 'Python.svg',
            'rb': 'RubyGems.svg',
            'java': 'Default.svg',
            'c': 'Default.svg',
            'cpp': 'C++.svg',
            'h': 'Default.svg',
            'hpp': 'C++.svg',
            'go': 'Go.svg',
            'rs': 'Default.svg',
            'php': 'PHP.svg',
            'html': 'DOM.svg',
            'htm': 'DOM.svg',
            'css': 'Stylus.svg',
            'scss': 'Stylus.svg',
            'sass': 'Stylus.svg',
            'less': 'Stylus.svg',
            'xml': 'Default.svg',
            'yaml': 'YAML.svg',
            'yml': 'YAML.svg',
            'md': 'MarkdownLint.svg',
            'markdown': 'MarkdownLint.svg',
            'txt': 'Default.svg',
            'pdf': 'Adobe-Acrobat.svg',
            'doc': 'Microsoft-Word.svg',
            'docx': 'Microsoft-Word.svg',
            'xls': 'Microsoft-Excel.svg',
            'xlsx': 'Microsoft-Excel.svg',
            'ppt': 'Microsoft-PowerPoint.svg',
            'pptx': 'Microsoft-PowerPoint.svg',
            'sql': 'SQLite.svg',
            'sh': 'Terminal.svg',
            'bash': 'Terminal.svg',
            'zsh': 'Terminal.svg',
            'png': 'Image.svg',
            'jpg': 'Image.svg',
            'jpeg': 'Image.svg',
            'gif': 'Image.svg',
            'svg': 'Default.svg',
            'webp': 'Image.svg',
            'ico': 'Image.svg',
            'zip': 'Brotli.svg',
            'tar': 'Brotli.svg',
            'gz': 'Brotli.svg',
            'rar': 'Brotli.svg',
            '7z': 'Brotli.svg',
            'mp4': 'Video.svg',
            'webm': 'Video.svg',
            'avi': 'Video.svg',
            'mov': 'Video.svg',
            'mp3': 'Audacity.svg',
            'wav': 'Audacity.svg',
            'ogg': 'Audacity.svg',
            'vue': 'Vue.svg',
            'svelte': 'Svelte.svg',
            'dockerfile': 'Docker.svg',
            'gradle': 'Gradle.svg',
            'toml': 'TOML.svg',
            'ini': 'Config.svg',
            'cfg': 'Config.svg',
            'conf': 'Config.svg',
            'env': 'dotenv.svg',
            'eslintrc': 'ESLint.svg',
            'prettierrc': 'Prettier.svg',
            'lua': 'Lua.svg',
            'kt': 'Kotlin.svg',
            'scala': 'Default.svg',
            'groovy': 'Groovy.svg',
            'r': 'R.svg',
            'jl': 'Julia.svg',
            'ex': 'Default.svg',
            'exs': 'Default.svg',
            'erl': 'Default.svg',
            'hs': 'Default.svg',
            'elm': 'Elm.svg',
            'clj': 'ClojureJS.svg',
            'cljs': 'ClojureJS.svg'
        },

        getIcon: function(mimeType, fileName) {
            var iconFile = 'Default.svg';

            if (fileName) {
                var ext = fileName.split('.').pop().toLowerCase();
                if (this.extensionIconMap[ext]) {
                    iconFile = this.extensionIconMap[ext];
                }
            }

            if (mimeType && this.fileIconMap[mimeType]) {
                iconFile = this.fileIconMap[mimeType];
            } else if (mimeType) {
                if (mimeType.indexOf('image') === 0) {
                    iconFile = 'Image.svg';
                } else if (mimeType.indexOf('video') === 0) {
                    iconFile = 'Video.svg';
                } else if (mimeType.indexOf('audio') === 0) {
                    iconFile = 'Audio.svg';
                } else if (mimeType.indexOf('text') === 0) {
                    iconFile = 'Default.svg';
                }
            }

            return '<img src="/static/file-icons/svg/' + iconFile + '" alt="" class="ai-chat-attachment-icon-img">';
        },

        formatSize: function(size) {
            if (size >= 1000000) {
                return (size / 1000000).toFixed(1) + ' MB';
            } else if (size >= 1000) {
                return Math.round(size / 1000) + ' KB';
            } else {
                return size + ' B';
            }
        },

        render: function(widget, tabId, tabs) {
            if (!tabId) {
                return;
            }

            for (var i = 0; i < tabs.length; i++) {
                if (tabs[i].id === tabId) {
                    AIChatTabState.saveToTab(tabs[i]);
                    AIChatState.saveTabs(tabs);
                    break;
                }
            }

            var attachments = AIChatTabState.getAttachments(tabId);
            var tabPanel = widget.querySelector('.ai-chat-tab-panel[data-tab-id="' + tabId + '"]');
            if (!tabPanel) {
                return;
            }
            var container = tabPanel.querySelector('.ai-chat-attachments');

            if (attachments.length === 0) {
                if (container) {
                    container.parentNode.removeChild(container);
                }
                return;
            }

            if (!container) {
                var inputArea = tabPanel.querySelector('.ai-chat-input-area');
                if (!inputArea) {
                    return;
                }
                container = document.createElement('div');
                container.className = 'ai-chat-attachments';
                inputArea.insertBefore(container, inputArea.firstChild);
            }

            var html = '';
            for (var i = 0; i < attachments.length; i++) {
                var att = attachments[i];
                var sizeStr = this.formatSize(att.size);
                var icon = this.getIcon(att.type, att.name);
                html += '<div class="ai-chat-attachment" data-attachment-id="' + att.id + '">';
                html += '<div class="ai-chat-attachment-icon">';
                html += icon;
                html += '</div>';
                html += '<div class="ai-chat-attachment-info">';
                html += '<div class="ai-chat-attachment-name">' + att.name + '</div>';
                html += '<div class="ai-chat-attachment-size">' + sizeStr + '</div>';
                html += '</div>';
                html += '<button class="ai-chat-attachment-remove" data-attachment-id="' + att.id + '" aria-label="Remove">';
                html += '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>';
                html += '</button>';
                html += '</div>';
            }
            container.innerHTML = html;
        },

        addFile: function(file, tabId, callback) {
            var reader = new FileReader();
            reader.onload = function(e) {
                AIChatTabState.createAttachmentFromFile(tabId, file, e.target.result);
                if (callback) {
                    callback();
                }
            };

            var isImage = file.type && file.type.indexOf('image') === 0;
            var isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
            var isWord = file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || 
                         file.name.toLowerCase().endsWith('.docx');

            if (isImage || isPdf || isWord) {
                reader.readAsDataURL(file);
            } else {
                reader.readAsText(file);
            }
        },

        showFileDialog: function(tabId, callback) {
            var self = this;
            var input = document.createElement('input');
            input.type = 'file';
            input.multiple = true;
            input.style.display = 'none';
            input.addEventListener('change', function(e) {
                var files = e.target.files;
                if (files && files.length > 0) {
                    var processed = 0;
                    for (var i = 0; i < files.length; i++) {
                        self.addFile(files[i], tabId, function() {
                            processed++;
                            if (processed === files.length && callback) {
                                callback();
                            }
                        });
                    }
                }
                document.body.removeChild(input);
            });
            document.body.appendChild(input);
            input.click();
        }
    };

    window.AIChatAttachments = AIChatAttachments;

})();
