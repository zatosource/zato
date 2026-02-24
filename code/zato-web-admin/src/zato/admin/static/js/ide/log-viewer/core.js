(function() {
    'use strict';

    var ZatoLogViewer = {

        instances: {},

        create: function(containerId, options) {
            var container = document.getElementById(containerId);
            if (!container) {
                return null;
            }

            var instance = {
                id: containerId,
                container: container,
                options: options || {},
                filePath: options.filePath || '',
                eventSource: null,
                isStreaming: false,
                autoScroll: true,
                lines: [],
                maxLines: options.maxLines || 10000,
                searchTerm: '',
                searchMatches: [],
                currentMatchIndex: -1,
                levelFilters: {
                    info: true,
                    warning: true,
                    error: true,
                    debug: true
                },
                timeRange: 'live'
            };

            this.instances[containerId] = instance;
            this.render(instance);
            this.bindEvents(instance);

            if (instance.filePath) {
                this.startStreaming(instance);
            }

            return instance;
        },

        getInstance: function(containerId) {
            return this.instances[containerId] || null;
        },

        destroy: function(containerId) {
            var instance = this.instances[containerId];
            if (instance) {
                this.stopStreaming(instance);
                if (instance.container) {
                    instance.container.innerHTML = '';
                }
                delete this.instances[containerId];
            }
        },

        render: function(instance) {
            var html = '';

            html += '<div class="zato-log-viewer">';
            html += '<div class="zato-log-viewer-content" id="' + instance.id + '-content"></div>';
            html += '<div class="zato-log-viewer-actionbar">';

            html += '<div class="zato-log-viewer-actionbar-left">';
            html += '<button class="zato-log-viewer-button zato-log-viewer-play-stop" data-action="play-stop" title="Play/Stop streaming">';
            html += '<span class="zato-log-viewer-icon-stop"></span>';
            html += '</button>';
            html += '<button class="zato-log-viewer-button zato-log-viewer-clear" data-action="clear" title="Clear buffer">';
            html += '<span class="zato-log-viewer-icon-clear"></span>';
            html += '</button>';
            html += '</div>';

            html += '<div class="zato-log-viewer-actionbar-center">';
            html += '<div class="zato-log-viewer-search-container">';
            html += '<input type="text" class="zato-log-viewer-search" placeholder="Search logs..." id="' + instance.id + '-search">';
            html += '<span class="zato-log-viewer-search-count" id="' + instance.id + '-search-count"></span>';
            html += '<button class="zato-log-viewer-button zato-log-viewer-search-prev" data-action="search-prev" title="Previous match">&#9650;</button>';
            html += '<button class="zato-log-viewer-button zato-log-viewer-search-next" data-action="search-next" title="Next match">&#9660;</button>';
            html += '</div>';
            html += '</div>';

            html += '<div class="zato-log-viewer-actionbar-right">';

            html += '<div class="zato-log-viewer-filters">';
            html += '<label class="zato-log-viewer-filter-label"><input type="checkbox" class="zato-log-viewer-filter" data-level="info" checked> <span class="zato-log-level-info">info</span></label>';
            html += '<label class="zato-log-viewer-filter-label"><input type="checkbox" class="zato-log-viewer-filter" data-level="warning" checked> <span class="zato-log-level-warning">warn</span></label>';
            html += '<label class="zato-log-viewer-filter-label"><input type="checkbox" class="zato-log-viewer-filter" data-level="error" checked> <span class="zato-log-level-error">error</span></label>';
            html += '<label class="zato-log-viewer-filter-label"><input type="checkbox" class="zato-log-viewer-filter" data-level="debug" checked> <span class="zato-log-level-debug">debug</span></label>';
            html += '</div>';

            html += '<div class="zato-log-viewer-time-picker">';
            html += '<select class="zato-log-viewer-time-select" id="' + instance.id + '-time-select">';
            html += '<option value="live">Live tail</option>';
            html += '<option value="15m">Past 15 minutes</option>';
            html += '<option value="1h">Past 1 hour</option>';
            html += '<option value="4h">Past 4 hours</option>';
            html += '<option value="1d">Past 1 day</option>';
            html += '<option value="2d">Past 2 days</option>';
            html += '<option value="7d">Past 7 days</option>';
            html += '<option value="15d">Past 15 days</option>';
            html += '<option value="1M">Past 1 month</option>';
            html += '</select>';
            html += '</div>';

            html += '</div>';

            html += '</div>';
            html += '</div>';

            instance.container.innerHTML = html;

            instance.contentEl = document.getElementById(instance.id + '-content');
            instance.searchInput = document.getElementById(instance.id + '-search');
            instance.searchCountEl = document.getElementById(instance.id + '-search-count');
            instance.timeSelect = document.getElementById(instance.id + '-time-select');
        },

        bindEvents: function(instance) {
            var self = this;
            var container = instance.container;

            container.addEventListener('click', function(e) {
                var button = e.target.closest('[data-action]');
                if (!button) {
                    return;
                }

                var action = button.getAttribute('data-action');

                if (action === 'play-stop') {
                    self.toggleStreaming(instance);
                } else if (action === 'clear') {
                    self.clearBuffer(instance);
                } else if (action === 'search-prev') {
                    self.searchPrev(instance);
                } else if (action === 'search-next') {
                    self.searchNext(instance);
                }
            });

            var filterCheckboxes = container.querySelectorAll('.zato-log-viewer-filter');
            filterCheckboxes.forEach(function(checkbox) {
                checkbox.addEventListener('change', function() {
                    var level = checkbox.getAttribute('data-level');
                    instance.levelFilters[level] = checkbox.checked;
                    self.applyFilters(instance);
                });
            });

            if (instance.searchInput) {
                instance.searchInput.addEventListener('input', function() {
                    instance.searchTerm = instance.searchInput.value;
                    self.performSearch(instance);
                });

                instance.searchInput.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') {
                        if (e.shiftKey) {
                            self.searchPrev(instance);
                        } else {
                            self.searchNext(instance);
                        }
                        e.preventDefault();
                    }
                });
            }

            if (instance.timeSelect) {
                instance.timeSelect.addEventListener('change', function() {
                    instance.timeRange = instance.timeSelect.value;
                    self.restartStreaming(instance);
                });
            }

            if (instance.contentEl) {
                instance.contentEl.addEventListener('scroll', function() {
                    var el = instance.contentEl;
                    var atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 50;
                    instance.autoScroll = atBottom;
                });

                instance.contentEl.addEventListener('keydown', function() {
                    instance.autoScroll = true;
                    self.scrollToBottom(instance);
                });
            }
        },

        startStreaming: function(instance) {
            var self = this;

            if (instance.eventSource) {
                instance.eventSource.close();
            }

            var levels = [];
            Object.keys(instance.levelFilters).forEach(function(level) {
                if (instance.levelFilters[level]) {
                    levels.push(level);
                }
            });

            var url = '/zato/ide/logs/stream/?path=' + encodeURIComponent(instance.filePath);
            url += '&levels=' + encodeURIComponent(levels.join(','));
            url += '&time_range=' + encodeURIComponent(instance.timeRange);

            instance.eventSource = new EventSource(url);
            instance.isStreaming = true;

            self.updatePlayStopButton(instance);

            instance.eventSource.onmessage = function(e) {
                if (e.data) {
                    try {
                        var parsed = JSON.parse(e.data);
                        self.addLine(instance, parsed);
                    } catch (err) {
                    }
                }
            };

            instance.eventSource.onopen = function() {
            };

            instance.eventSource.onerror = function(e) {
                if (instance.eventSource.readyState === EventSource.CLOSED) {
                    instance.isStreaming = false;
                    self.updatePlayStopButton(instance);
                }
            };
        },

        stopStreaming: function(instance) {
            if (instance.eventSource) {
                instance.eventSource.close();
                instance.eventSource = null;
            }
            instance.isStreaming = false;
            this.updatePlayStopButton(instance);
        },

        toggleStreaming: function(instance) {
            if (instance.isStreaming) {
                this.stopStreaming(instance);
            } else {
                this.startStreaming(instance);
            }
        },

        restartStreaming: function(instance) {
            this.clearBuffer(instance);
            if (instance.isStreaming) {
                this.stopStreaming(instance);
            }
            this.startStreaming(instance);
        },

        updatePlayStopButton: function(instance) {
            var button = instance.container.querySelector('.zato-log-viewer-play-stop');
            if (!button) {
                return;
            }

            if (instance.isStreaming) {
                button.innerHTML = '<span class="zato-log-viewer-icon-stop"></span>';
                button.title = 'Stop streaming';
            } else {
                button.innerHTML = '<span class="zato-log-viewer-icon-play"></span>';
                button.title = 'Start streaming';
            }
        },

        addLine: function(instance, lineData) {
            instance.lines.push(lineData);

            if (instance.lines.length > instance.maxLines) {
                instance.lines.shift();
                if (instance.contentEl && instance.contentEl.firstChild) {
                    instance.contentEl.removeChild(instance.contentEl.firstChild);
                }
            }

            if (this.shouldShowLine(instance, lineData)) {
                this.renderLine(instance, lineData);
            }

            if (instance.autoScroll) {
                this.scrollToBottom(instance);
            }
        },


        shouldShowLine: function(instance, lineData) {
            if (lineData.level && !instance.levelFilters[lineData.level]) {
                return false;
            }
            return true;
        },

        renderLine: function(instance, lineData) {
            if (!instance.contentEl) {
                return;
            }

            var lineEl = document.createElement('div');
            lineEl.className = 'zato-log-line';

            if (lineData.level) {
                lineEl.classList.add('zato-log-line-' + lineData.level);
            }

            var html = '';

            if (lineData.timestamp) {
                html += '<span class="zato-log-timestamp">' + this.escapeHtml(lineData.timestamp) + '</span>';
                html += '<span class="zato-log-separator"> - </span>';
            }

            if (lineData.level) {
                html += '<span class="zato-log-level zato-log-level-' + lineData.level + '">' + this.escapeHtml(lineData.level.toUpperCase()) + '</span>';
                html += '<span class="zato-log-separator"> - </span>';
            }

            if (lineData.pid) {
                html += '<span class="zato-log-pid">' + this.escapeHtml(lineData.pid) + '</span>';
                if (lineData.thread) {
                    html += '<span class="zato-log-separator">:</span>';
                    html += '<span class="zato-log-thread">' + this.escapeHtml(lineData.thread) + '</span>';
                }
                html += '<span class="zato-log-separator"> - </span>';
            }

            if (lineData.logger) {
                html += '<span class="zato-log-logger">' + this.escapeHtml(lineData.logger) + '</span>';
                html += '<span class="zato-log-separator"> - </span>';
            }

            if (lineData.message) {
                html += '<span class="zato-log-message">' + this.escapeHtml(lineData.message) + '</span>';
            } else if (!lineData.timestamp) {
                html += '<span class="zato-log-message">' + this.escapeHtml(lineData.raw) + '</span>';
            }

            lineEl.innerHTML = html;
            lineEl.setAttribute('data-raw', lineData.raw);

            instance.contentEl.appendChild(lineEl);
        },

        escapeHtml: function(text) {
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        scrollToBottom: function(instance) {
            if (instance.contentEl) {
                instance.contentEl.scrollTop = instance.contentEl.scrollHeight;
            }
        },

        clearBuffer: function(instance) {
            instance.lines = [];
            if (instance.contentEl) {
                instance.contentEl.innerHTML = '';
            }
            instance.searchMatches = [];
            instance.currentMatchIndex = -1;
            this.updateSearchCount(instance);
        },

        applyFilters: function(instance) {
            if (!instance.contentEl) {
                return;
            }

            instance.contentEl.innerHTML = '';

            instance.lines.forEach(function(lineData) {
                if (this.shouldShowLine(instance, lineData)) {
                    this.renderLine(instance, lineData);
                }
            }, this);

            if (instance.autoScroll) {
                this.scrollToBottom(instance);
            }

            this.performSearch(instance);
        },

        performSearch: function(instance) {
            instance.searchMatches = [];
            instance.currentMatchIndex = -1;

            var allLines = instance.contentEl.querySelectorAll('.zato-log-line');
            allLines.forEach(function(lineEl) {
                lineEl.classList.remove('zato-log-line-match', 'zato-log-line-current-match');
            });

            if (!instance.searchTerm) {
                this.updateSearchCount(instance);
                return;
            }

            var searchLower = instance.searchTerm.toLowerCase();

            allLines.forEach(function(lineEl, index) {
                var raw = lineEl.getAttribute('data-raw') || '';
                if (raw.toLowerCase().indexOf(searchLower) !== -1) {
                    lineEl.classList.add('zato-log-line-match');
                    instance.searchMatches.push(index);
                }
            });

            this.updateSearchCount(instance);

            if (instance.searchMatches.length > 0) {
                instance.currentMatchIndex = 0;
                this.highlightCurrentMatch(instance);
            }
        },

        searchNext: function(instance) {
            if (instance.searchMatches.length === 0) {
                return;
            }

            instance.currentMatchIndex = (instance.currentMatchIndex + 1) % instance.searchMatches.length;
            this.highlightCurrentMatch(instance);
        },

        searchPrev: function(instance) {
            if (instance.searchMatches.length === 0) {
                return;
            }

            instance.currentMatchIndex = (instance.currentMatchIndex - 1 + instance.searchMatches.length) % instance.searchMatches.length;
            this.highlightCurrentMatch(instance);
        },

        highlightCurrentMatch: function(instance) {
            var allLines = instance.contentEl.querySelectorAll('.zato-log-line');
            allLines.forEach(function(lineEl) {
                lineEl.classList.remove('zato-log-line-current-match');
            });

            if (instance.currentMatchIndex >= 0 && instance.currentMatchIndex < instance.searchMatches.length) {
                var lineIndex = instance.searchMatches[instance.currentMatchIndex];
                var lineEl = allLines[lineIndex];
                if (lineEl) {
                    lineEl.classList.add('zato-log-line-current-match');
                    lineEl.scrollIntoView({ block: 'center', behavior: 'smooth' });
                    instance.autoScroll = false;
                }
            }

            this.updateSearchCount(instance);
        },

        updateSearchCount: function(instance) {
            if (!instance.searchCountEl) {
                return;
            }

            if (instance.searchMatches.length === 0) {
                if (instance.searchTerm) {
                    instance.searchCountEl.textContent = '0 results';
                } else {
                    instance.searchCountEl.textContent = '';
                }
            } else {
                instance.searchCountEl.textContent = (instance.currentMatchIndex + 1) + ' of ' + instance.searchMatches.length;
            }
        },

        setFilePath: function(instance, filePath) {
            instance.filePath = filePath;
            this.restartStreaming(instance);
        }
    };

    window.ZatoLogViewer = ZatoLogViewer;

})();
