(function() {
    'use strict';

    var STORAGE_KEY_FIND_HISTORY = 'zato.ide.search.find-history';
    var STORAGE_KEY_REPLACE_HISTORY = 'zato.ide.search.replace-history';
    var MAX_HISTORY_ITEMS = 20;

    var ZatoIDESearch = {

        instances: {},

        create: function(instance) {
            var self = this;
            var searchInstance = {
                ideInstance: instance,
                element: null,
                isVisible: false,
                isReplaceVisible: false,
                caseSensitive: false,
                wholeWord: false,
                searchInSelection: false,
                searchRange: null,
                searchRangeMarker: null,
                findHistory: self.loadHistory(STORAGE_KEY_FIND_HISTORY),
                replaceHistory: self.loadHistory(STORAGE_KEY_REPLACE_HISTORY),
                findHistoryIndex: -1,
                replaceHistoryIndex: -1
            };

            self.instances[instance.id] = searchInstance;
            self.render(searchInstance);
            self.bindEvents(searchInstance);

            return searchInstance;
        },

        getInstance: function(ideInstance) {
            return this.instances[ideInstance.id];
        },

        render: function(searchInstance) {
            var html = '';
            html += '<div class="zato-ide-search-widget">';
            html += '<div class="zato-ide-search-header">';
            html += '<span class="zato-ide-search-title">Find and replace</span>';
            html += '<button class="zato-ide-search-close" title="Close (Escape)">&times;</button>';
            html += '</div>';
            html += '<div class="zato-ide-search-body">';

            html += '<div class="zato-ide-search-row zato-ide-search-find-row">';
            html += '<input type="text" class="zato-ide-search-input zato-ide-search-find-input" placeholder="Find">';
            html += '<button class="zato-ide-search-button zato-ide-search-prev" title="Previous (Shift+Enter)">&#9650;</button>';
            html += '<button class="zato-ide-search-button zato-ide-search-next" title="Next (Enter)">&#9660;</button>';
            html += '<span class="zato-ide-search-counter"></span>';
            html += '<button class="zato-ide-search-expand-button" title="Toggle replace">&#9662;</button>';
            html += '</div>';

            html += '<div class="zato-ide-search-row zato-ide-search-replace-row" style="display: none;">';
            html += '<input type="text" class="zato-ide-search-input zato-ide-search-replace-input" placeholder="Replace with">';
            html += '<button class="zato-ide-search-button zato-ide-search-replace-one" title="Replace">Replace</button>';
            html += '<button class="zato-ide-search-button zato-ide-search-replace-all" title="Replace all">All</button>';
            html += '</div>';

            html += '<div class="zato-ide-search-options">';
            html += '<label class="zato-ide-search-option"><input type="checkbox" class="zato-ide-search-case"> Match case</label>';
            html += '<label class="zato-ide-search-option"><input type="checkbox" class="zato-ide-search-word"> Whole word</label>';
            html += '<label class="zato-ide-search-option"><input type="checkbox" class="zato-ide-search-selection"> In selection</label>';
            html += '</div>';

            html += '</div>';
            html += '<div class="zato-ide-search-resize-handle"></div>';
            html += '</div>';

            var container = document.createElement('div');
            container.innerHTML = html;
            var widget = container.firstChild;

            var ideContainer = searchInstance.ideInstance.container;
            ideContainer.appendChild(widget);

            searchInstance.element = widget;
            searchInstance.findInput = widget.querySelector('.zato-ide-search-find-input');
            searchInstance.replaceInput = widget.querySelector('.zato-ide-search-replace-input');
            searchInstance.replaceRow = widget.querySelector('.zato-ide-search-replace-row');
            searchInstance.expandButton = widget.querySelector('.zato-ide-search-expand-button');
            searchInstance.counter = widget.querySelector('.zato-ide-search-counter');
            searchInstance.caseCheckbox = widget.querySelector('.zato-ide-search-case');
            searchInstance.wordCheckbox = widget.querySelector('.zato-ide-search-word');
            searchInstance.selectionCheckbox = widget.querySelector('.zato-ide-search-selection');
        },

        bindEvents: function(searchInstance) {
            var self = this;
            var widget = searchInstance.element;

            var closeButton = widget.querySelector('.zato-ide-search-close');
            closeButton.addEventListener('click', function() {
                self.hide(searchInstance);
            });

            searchInstance.expandButton.addEventListener('click', function() {
                self.toggleReplace(searchInstance);
            });

            var prevButton = widget.querySelector('.zato-ide-search-prev');
            prevButton.addEventListener('click', function() {
                self.findPrev(searchInstance);
            });

            var nextButton = widget.querySelector('.zato-ide-search-next');
            nextButton.addEventListener('click', function() {
                self.findNext(searchInstance);
            });

            var replaceOneButton = widget.querySelector('.zato-ide-search-replace-one');
            replaceOneButton.addEventListener('click', function() {
                self.replaceOne(searchInstance);
            });

            var replaceAllButton = widget.querySelector('.zato-ide-search-replace-all');
            replaceAllButton.addEventListener('click', function() {
                self.replaceAll(searchInstance);
            });

            searchInstance.findInput.addEventListener('input', function() {
                self.find(searchInstance, false, false, true);
            });

            searchInstance.findInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    if (e.shiftKey) {
                        self.findPrev(searchInstance);
                    } else {
                        self.findNext(searchInstance);
                    }
                    self.addToHistory(searchInstance, 'find', searchInstance.findInput.value);
                } else if (e.key === 'Escape') {
                    e.preventDefault();
                    self.hide(searchInstance);
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    self.navigateHistory(searchInstance, 'find', -1);
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    self.navigateHistory(searchInstance, 'find', 1);
                }
            });

            searchInstance.replaceInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    if (e.shiftKey) {
                        self.replaceAll(searchInstance);
                    } else {
                        self.replaceOne(searchInstance);
                    }
                    self.addToHistory(searchInstance, 'replace', searchInstance.replaceInput.value);
                } else if (e.key === 'Escape') {
                    e.preventDefault();
                    self.hide(searchInstance);
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    self.navigateHistory(searchInstance, 'replace', -1);
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    self.navigateHistory(searchInstance, 'replace', 1);
                }
            });

            searchInstance.caseCheckbox.addEventListener('change', function() {
                searchInstance.caseSensitive = this.checked;
                self.find(searchInstance, false, false, true);
            });

            searchInstance.wordCheckbox.addEventListener('change', function() {
                searchInstance.wholeWord = this.checked;
                self.find(searchInstance, false, false, true);
            });

            searchInstance.selectionCheckbox.addEventListener('change', function() {
                searchInstance.searchInSelection = this.checked;
                if (this.checked) {
                    self.setSearchRange(searchInstance);
                } else {
                    self.clearSearchRange(searchInstance);
                }
                self.find(searchInstance, false, false, true);
            });

            self.makeDraggable(searchInstance);
            self.makeResizable(searchInstance);
        },

        makeDraggable: function(searchInstance) {
            var widget = searchInstance.element;
            var header = widget.querySelector('.zato-ide-search-header');
            var isDragging = false;
            var startX, startY, startLeft, startTop;

            header.addEventListener('mousedown', function(e) {
                if (e.target.classList.contains('zato-ide-search-close')) {
                    return;
                }
                isDragging = true;
                startX = e.clientX;
                startY = e.clientY;
                var rect = widget.getBoundingClientRect();
                startLeft = rect.left;
                startTop = rect.top;
                e.preventDefault();
            });

            document.addEventListener('mousemove', function(e) {
                if (!isDragging) { return; }
                var dx = e.clientX - startX;
                var dy = e.clientY - startY;
                widget.style.left = (startLeft + dx) + 'px';
                widget.style.top = (startTop + dy) + 'px';
                widget.style.right = 'auto';
            });

            document.addEventListener('mouseup', function() {
                isDragging = false;
            });
        },

        makeResizable: function(searchInstance) {
            var widget = searchInstance.element;
            var handle = widget.querySelector('.zato-ide-search-resize-handle');
            var isResizing = false;
            var startX, startY, startWidth, startHeight;

            handle.addEventListener('mousedown', function(e) {
                isResizing = true;
                startX = e.clientX;
                startY = e.clientY;
                startWidth = widget.offsetWidth;
                startHeight = widget.offsetHeight;
                e.preventDefault();
            });

            document.addEventListener('mousemove', function(e) {
                if (!isResizing) { return; }
                var dx = e.clientX - startX;
                var dy = e.clientY - startY;
                var newWidth = Math.max(280, startWidth + dx);
                var newHeight = Math.max(100, startHeight + dy);
                widget.style.width = newWidth + 'px';
                widget.style.height = newHeight + 'px';
            });

            document.addEventListener('mouseup', function() {
                isResizing = false;
            });
        },

        show: function(searchInstance, isReplace) {
            var widget = searchInstance.element;
            widget.style.display = 'flex';
            searchInstance.isVisible = true;

            if (isReplace && !searchInstance.isReplaceVisible) {
                this.toggleReplace(searchInstance);
            }

            var aceEditor = searchInstance.ideInstance.codeEditor && searchInstance.ideInstance.codeEditor.aceEditor;
            if (aceEditor) {
                var selectedText = aceEditor.getSelectedText();
                if (selectedText && selectedText.indexOf('\n') === -1) {
                    searchInstance.findInput.value = selectedText;
                }
            }

            searchInstance.findInput.focus();
            searchInstance.findInput.select();
            searchInstance.findHistoryIndex = -1;
            searchInstance.replaceHistoryIndex = -1;

            this.find(searchInstance, false, false, true);
        },

        hide: function(searchInstance) {
            var widget = searchInstance.element;
            widget.style.display = 'none';
            searchInstance.isVisible = false;
            this.clearSearchRange(searchInstance);

            var aceEditor = searchInstance.ideInstance.codeEditor && searchInstance.ideInstance.codeEditor.aceEditor;
            if (aceEditor) {
                aceEditor.focus();
            }
        },

        toggle: function(searchInstance) {
            if (searchInstance.isVisible) {
                this.hide(searchInstance);
            } else {
                this.show(searchInstance, false);
            }
        },

        toggleReplace: function(searchInstance) {
            searchInstance.isReplaceVisible = !searchInstance.isReplaceVisible;
            searchInstance.replaceRow.style.display = searchInstance.isReplaceVisible ? 'flex' : 'none';
            searchInstance.expandButton.innerHTML = searchInstance.isReplaceVisible ? '&#9652;' : '&#9662;';
        },

        find: function(searchInstance, skipCurrent, backwards, preventScroll) {
            var aceEditor = searchInstance.ideInstance.codeEditor && searchInstance.ideInstance.codeEditor.aceEditor;
            if (!aceEditor) { return; }

            var needle = searchInstance.findInput.value;
            if (!needle) {
                searchInstance.counter.textContent = '';
                return;
            }

            var options = {
                skipCurrent: skipCurrent,
                backwards: backwards,
                wrap: true,
                caseSensitive: searchInstance.caseSensitive,
                wholeWord: searchInstance.wholeWord,
                preventScroll: preventScroll,
                range: searchInstance.searchRange
            };

            var range = aceEditor.find(needle, options);
            var noMatch = !range && needle;

            if (noMatch) {
                searchInstance.findInput.classList.add('no-match');
            } else {
                searchInstance.findInput.classList.remove('no-match');
            }

            this.updateCounter(searchInstance);
        },

        findNext: function(searchInstance) {
            this.find(searchInstance, true, false, false);
        },

        findPrev: function(searchInstance) {
            this.find(searchInstance, true, true, false);
        },

        replaceOne: function(searchInstance) {
            var aceEditor = searchInstance.ideInstance.codeEditor && searchInstance.ideInstance.codeEditor.aceEditor;
            if (!aceEditor || aceEditor.getReadOnly()) { return; }

            var replacement = searchInstance.replaceInput.value;
            aceEditor.replace(replacement);
            this.addToHistory(searchInstance, 'replace', replacement);
            this.findNext(searchInstance);
        },

        replaceAll: function(searchInstance) {
            var aceEditor = searchInstance.ideInstance.codeEditor && searchInstance.ideInstance.codeEditor.aceEditor;
            if (!aceEditor || aceEditor.getReadOnly()) { return; }

            var needle = searchInstance.findInput.value;
            if (!needle) { return; }

            var replacement = searchInstance.replaceInput.value;

            aceEditor.replaceAll(replacement, {
                needle: needle,
                caseSensitive: searchInstance.caseSensitive,
                wholeWord: searchInstance.wholeWord,
                range: searchInstance.searchRange
            });

            this.addToHistory(searchInstance, 'find', needle);
            this.addToHistory(searchInstance, 'replace', replacement);
            this.updateCounter(searchInstance);
        },

        setSearchRange: function(searchInstance) {
            var aceEditor = searchInstance.ideInstance.codeEditor && searchInstance.ideInstance.codeEditor.aceEditor;
            if (!aceEditor) { return; }

            var range = aceEditor.getSelectionRange();
            if (range && !range.isEmpty()) {
                searchInstance.searchRange = range;
                searchInstance.searchRangeMarker = aceEditor.session.addMarker(range, 'ace_active-line', 'background');
            }
        },

        clearSearchRange: function(searchInstance) {
            var aceEditor = searchInstance.ideInstance.codeEditor && searchInstance.ideInstance.codeEditor.aceEditor;
            if (!aceEditor) { return; }

            if (searchInstance.searchRangeMarker) {
                aceEditor.session.removeMarker(searchInstance.searchRangeMarker);
                searchInstance.searchRangeMarker = null;
            }
            searchInstance.searchRange = null;
        },

        updateCounter: function(searchInstance) {
            var aceEditor = searchInstance.ideInstance.codeEditor && searchInstance.ideInstance.codeEditor.aceEditor;
            if (!aceEditor) { return; }

            var needle = searchInstance.findInput.value;
            if (!needle) {
                searchInstance.counter.textContent = '';
                return;
            }

            var content = searchInstance.searchRange
                ? aceEditor.session.getTextRange(searchInstance.searchRange)
                : aceEditor.getValue();

            var flags = searchInstance.caseSensitive ? 'g' : 'gi';
            var escapedNeedle = needle.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

            if (searchInstance.wholeWord) {
                escapedNeedle = '\\b' + escapedNeedle + '\\b';
            }

            var regex;
            try {
                regex = new RegExp(escapedNeedle, flags);
            } catch (e) {
                searchInstance.counter.textContent = '';
                return;
            }

            var matches = content.match(regex);
            var total = matches ? matches.length : 0;

            if (total === 0) {
                searchInstance.counter.textContent = 'No results';
            } else {
                var cursorPos = aceEditor.getCursorPosition();
                var textBeforeCursor = aceEditor.session.getTextRange({
                    start: { row: 0, column: 0 },
                    end: cursorPos
                });
                var matchesBefore = textBeforeCursor.match(regex);
                var current = matchesBefore ? matchesBefore.length : 0;
                searchInstance.counter.textContent = current + ' of ' + total;
            }
        },

        loadHistory: function(storageKey) {
            try {
                var data = localStorage.getItem(storageKey);
                if (data) {
                    return JSON.parse(data);
                }
            } catch (e) {
                console.debug('[ZatoIDESearch] Failed to load history:', e);
            }
            return [];
        },

        saveHistory: function(storageKey, history) {
            try {
                localStorage.setItem(storageKey, JSON.stringify(history));
            } catch (e) {
                console.debug('[ZatoIDESearch] Failed to save history:', e);
            }
        },

        addToHistory: function(searchInstance, type, value) {
            if (!value || !value.trim()) { return; }

            var history, storageKey;
            if (type === 'find') {
                history = searchInstance.findHistory;
                storageKey = STORAGE_KEY_FIND_HISTORY;
            } else {
                history = searchInstance.replaceHistory;
                storageKey = STORAGE_KEY_REPLACE_HISTORY;
            }

            var index = history.indexOf(value);
            if (index !== -1) {
                history.splice(index, 1);
            }

            history.unshift(value);

            if (history.length > MAX_HISTORY_ITEMS) {
                history.pop();
            }

            this.saveHistory(storageKey, history);
        },

        navigateHistory: function(searchInstance, type, direction) {
            var history, input, indexProp;
            if (type === 'find') {
                history = searchInstance.findHistory;
                input = searchInstance.findInput;
                indexProp = 'findHistoryIndex';
            } else {
                history = searchInstance.replaceHistory;
                input = searchInstance.replaceInput;
                indexProp = 'replaceHistoryIndex';
            }

            if (history.length === 0) { return; }

            var newIndex = searchInstance[indexProp] + direction;
            if (newIndex < 0) {
                newIndex = 0;
            } else if (newIndex >= history.length) {
                newIndex = history.length - 1;
            }

            searchInstance[indexProp] = newIndex;
            input.value = history[newIndex];

            if (type === 'find') {
                this.find(searchInstance, false, false, true);
            }
        }
    };

    window.ZatoIDESearch = ZatoIDESearch;

})();
