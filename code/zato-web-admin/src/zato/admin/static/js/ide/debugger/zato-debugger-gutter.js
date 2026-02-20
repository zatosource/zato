(function() {
    'use strict';

    /**
     * ZatoDebuggerGutter - ACE editor gutter integration for breakpoints.
     *
     * Handles:
     * - Breakpoint markers in the gutter
     * - Click to toggle breakpoints
     * - Current execution line highlighting
     * - Conditional breakpoint editing
     */
    var ZatoDebuggerGutter = {

        instances: {},

        markerIds: {},

        create: function(aceEditor, debuggerInstance, options) {
            console.log('[Gutter] create: START');
            console.log('[Gutter] create: aceEditor=' + (aceEditor ? 'exists' : 'null'));
            console.log('[Gutter] create: aceEditor.container.id=' + (aceEditor && aceEditor.container ? aceEditor.container.id : 'N/A'));
            console.log('[Gutter] create: debuggerInstance=' + (debuggerInstance ? 'exists' : 'null'));
            console.log('[Gutter] create: options=' + JSON.stringify(options));
            console.log('[Gutter] create: existing instances=' + JSON.stringify(Object.keys(this.instances)));
            console.log('[Gutter] create: stack trace=', new Error().stack);

            var instanceId = 'gutter-' + Date.now();

            var loadedBreakpoints = this.loadBreakpointsFromStorage();
            console.log('[Gutter] create: loadedBreakpoints=' + JSON.stringify(loadedBreakpoints));

            var instance = {
                id: instanceId,
                editor: aceEditor,
                debugger: debuggerInstance,
                options: options || {},
                currentLineMarkerId: null,
                breakpointDecorations: {},
                localBreakpoints: loadedBreakpoints
            };

            this.instances[instanceId] = instance;
            this.bindEvents(instance);
            this.applyStyles(instance);
            console.log('[Gutter] create: calling updateBreakpointMarkers');
            this.updateBreakpointMarkers(instance);

            console.log('[Gutter] create: END, instanceId=' + instanceId);
            return instance;
        },

        getInstance: function(instanceId) {
            return this.instances[instanceId] || null;
        },

        destroy: function(instanceId) {
            var instance = this.instances[instanceId];
            if (instance) {
                this.clearAllMarkers(instance);
                delete this.instances[instanceId];
            }
        },

        bindEvents: function(instance) {
            console.log('[Gutter] bindEvents: START instance.id=' + instance.id);
            var self = this;
            var editor = instance.editor;
            var gutter = editor.renderer.$gutter;
            console.log('[Gutter] bindEvents: gutter element=' + (gutter ? 'exists' : 'null'));
            console.log('[Gutter] bindEvents: gutter.id=' + (gutter ? gutter.id : 'N/A'));
            console.log('[Gutter] bindEvents: gutter existing listeners=' + (gutter._zatoGutterBound ? 'YES ALREADY BOUND' : 'no'));

            if (gutter._zatoGutterBound) {
                console.log('[Gutter] bindEvents: SKIPPING - already bound');
                return;
            }
            gutter._zatoGutterBound = true;

            gutter.addEventListener('click', function(e) {
                console.log('[Gutter] click event fired, instance.id=' + instance.id);
                e.preventDefault();
                e.stopPropagation();
                self.handleGutterClick(instance, e);
            });

            gutter.addEventListener('contextmenu', function(e) {
                self.handleGutterContextMenu(instance, e);
            });

            if (instance.debugger) {
                ZatoDebuggerCore.on(instance.debugger, 'onStateChange', function(data) {
                    self.updateCurrentLineMarker(instance);
                });

                ZatoDebuggerCore.on(instance.debugger, 'onCallStackUpdate', function(data) {
                    self.updateCurrentLineMarker(instance);
                });
            }
        },

        handleGutterClick: function(instance, event) {
            console.log('[Gutter] handleGutterClick: START');
            console.log('[Gutter] handleGutterClick: event.target.tagName=' + event.target.tagName);
            console.log('[Gutter] handleGutterClick: event.target.className=' + event.target.className);
            console.log('[Gutter] handleGutterClick: event.clientY=' + event.clientY);

            var editor = instance.editor;

            var gutterEl = editor.renderer.$gutter;
            var gutterRect = gutterEl.getBoundingClientRect();
            var relativeY = event.clientY - gutterRect.top;
            var firstVisibleRow = editor.renderer.getFirstVisibleRow();
            var lineHeight = editor.renderer.lineHeight;
            var clickedRow = firstVisibleRow + Math.floor(relativeY / lineHeight);

            console.log('[Gutter] handleGutterClick: gutterRect.top=' + gutterRect.top);
            console.log('[Gutter] handleGutterClick: relativeY=' + relativeY);
            console.log('[Gutter] handleGutterClick: firstVisibleRow=' + firstVisibleRow);
            console.log('[Gutter] handleGutterClick: lineHeight=' + lineHeight);
            console.log('[Gutter] handleGutterClick: clickedRow=' + clickedRow);

            var row = clickedRow;

            if (isNaN(row)) {
                console.log('[Gutter] handleGutterClick: row is NaN, returning');
                return;
            }

            var line = row + 1;
            var file = this.getCurrentFile(instance);
            console.log('[Gutter] handleGutterClick: line=' + line + ' file=' + file);
            console.log('[Gutter] handleGutterClick: instance.debugger=' + (instance.debugger ? 'exists' : 'null'));

            if (instance.debugger) {
                console.log('[Gutter] handleGutterClick: calling ZatoDebuggerCore.toggleBreakpoint');
                var bp = ZatoDebuggerCore.toggleBreakpoint(instance.debugger, file, line);
                console.log('[Gutter] handleGutterClick: toggleBreakpoint returned=' + JSON.stringify(bp));
                this.updateBreakpointMarkers(instance);
            } else {
                console.log('[Gutter] handleGutterClick: calling toggleLocalBreakpoint');
                this.toggleLocalBreakpoint(instance, file, line);
            }
            console.log('[Gutter] handleGutterClick: END');
        },

        toggleLocalBreakpoint: function(instance, file, line) {
            console.log('[Gutter] toggleLocalBreakpoint: file=' + file + ' line=' + line);
            if (!instance.localBreakpoints) {
                instance.localBreakpoints = this.loadBreakpointsFromStorage();
                console.log('[Gutter] toggleLocalBreakpoint: loaded from storage=' + JSON.stringify(instance.localBreakpoints));
            }
            if (!instance.localBreakpoints[file]) {
                instance.localBreakpoints[file] = {};
            }

            var bp = instance.localBreakpoints[file][line];
            if (bp) {
                if (bp.enabled) {
                    console.log('[Gutter] toggleLocalBreakpoint: disabling breakpoint at line ' + line);
                    bp.enabled = false;
                } else {
                    console.log('[Gutter] toggleLocalBreakpoint: removing breakpoint at line ' + line);
                    delete instance.localBreakpoints[file][line];
                }
            } else {
                console.log('[Gutter] toggleLocalBreakpoint: adding breakpoint at line ' + line);
                instance.localBreakpoints[file][line] = { line: line, enabled: true };
            }
            console.log('[Gutter] toggleLocalBreakpoint: localBreakpoints[' + file + ']=' + JSON.stringify(instance.localBreakpoints[file]));
            this.saveBreakpointsToStorage(instance.localBreakpoints);
            this.updateBreakpointMarkers(instance);
        },

        loadBreakpointsFromStorage: function() {
            try {
                var stored = localStorage.getItem('zato-ide-breakpoints');
                if (stored) {
                    return JSON.parse(stored);
                }
            } catch (e) {
                console.error('[DebuggerGutter] Failed to load breakpoints from storage:', e);
            }
            return {};
        },

        saveBreakpointsToStorage: function(breakpoints) {
            try {
                localStorage.setItem('zato-ide-breakpoints', JSON.stringify(breakpoints));
            } catch (e) {
                console.error('[DebuggerGutter] Failed to save breakpoints to storage:', e);
            }
        },

        handleGutterContextMenu: function(instance, event) {
            event.preventDefault();

            var editor = instance.editor;
            var target = event.target;

            if (!target.classList.contains('ace_gutter-cell')) {
                target = target.closest('.ace_gutter-cell');
            }

            if (!target) {
                return;
            }

            var row = parseInt(target.textContent, 10) - 1;
            if (isNaN(row)) {
                return;
            }

            var line = row + 1;
            var file = this.getCurrentFile(instance);

            this.showBreakpointContextMenu(instance, event.clientX, event.clientY, file, line);
        },

        showBreakpointContextMenu: function(instance, x, y, file, line) {
            var self = this;
            var existingMenu = document.querySelector('.zato-debugger-bp-context-menu');
            if (existingMenu) {
                existingMenu.remove();
            }

            var bp = instance.debugger ? ZatoDebuggerCore.getBreakpoint(instance.debugger, file, line) : null;

            var menu = document.createElement('div');
            menu.className = 'zato-debugger-bp-context-menu';
            menu.style.position = 'fixed';
            menu.style.left = x + 'px';
            menu.style.top = y + 'px';

            var items = [];
            var localBp = instance.localBreakpoints && instance.localBreakpoints[file] ? instance.localBreakpoints[file][line] : null;

            if (bp || localBp) {
                items.push({ label: 'Remove breakpoint', action: 'remove' });
                var isEnabled = bp ? bp.enabled : (localBp ? localBp.enabled : true);
                items.push({ label: isEnabled ? 'Disable breakpoint' : 'Enable breakpoint', action: 'toggle-enable' });
                items.push({ label: 'Edit condition...', action: 'edit-condition' });
            } else {
                items.push({ label: 'Add breakpoint', action: 'add' });
                items.push({ label: 'Add conditional breakpoint...', action: 'add-conditional' });
            }

            items.push({ separator: true });
            items.push({ label: 'Disable all breakpoints', action: 'disable-all' });
            items.push({ label: 'Clear all breakpoints', action: 'clear-all' });

            for (var i = 0; i < items.length; i++) {
                var item = items[i];
                if (item.separator) {
                    var sep = document.createElement('div');
                    sep.className = 'zato-debugger-bp-context-menu-separator';
                    menu.appendChild(sep);
                } else {
                    var itemEl = document.createElement('div');
                    itemEl.className = 'zato-debugger-bp-context-menu-item';
                    itemEl.textContent = item.label;
                    itemEl.setAttribute('data-action', item.action);
                    menu.appendChild(itemEl);
                }
            }

            document.body.appendChild(menu);

            menu.addEventListener('click', function(e) {
                var actionEl = e.target.closest('[data-action]');
                if (actionEl) {
                    var action = actionEl.getAttribute('data-action');
                    self.handleBreakpointAction(instance, action, file, line);
                }
                menu.remove();
            });

            var closeMenu = function(e) {
                if (!menu.contains(e.target)) {
                    menu.remove();
                    document.removeEventListener('click', closeMenu);
                }
            };

            setTimeout(function() {
                document.addEventListener('click', closeMenu);
            }, 0);
        },

        handleBreakpointAction: function(instance, action, file, line) {
            var self = this;

            if (instance.debugger) {
                switch (action) {
                    case 'add':
                        ZatoDebuggerCore.addBreakpoint(instance.debugger, file, line);
                        break;
                    case 'remove':
                        ZatoDebuggerCore.removeBreakpoint(instance.debugger, file, line);
                        break;
                    case 'toggle-enable':
                        var bp = ZatoDebuggerCore.getBreakpoint(instance.debugger, file, line);
                        if (bp) {
                            ZatoDebuggerCore.enableBreakpoint(instance.debugger, file, line, !bp.enabled);
                        }
                        break;
                    case 'add-conditional':
                    case 'edit-condition':
                        this.showConditionDialog(instance, file, line);
                        break;
                }
            } else {
                switch (action) {
                    case 'add':
                        if (!instance.localBreakpoints) {
                            instance.localBreakpoints = {};
                        }
                        if (!instance.localBreakpoints[file]) {
                            instance.localBreakpoints[file] = {};
                        }
                        instance.localBreakpoints[file][line] = { line: line, enabled: true };
                        this.saveBreakpointsToStorage(instance.localBreakpoints);
                        break;
                    case 'remove':
                        if (instance.localBreakpoints && instance.localBreakpoints[file]) {
                            delete instance.localBreakpoints[file][line];
                            this.saveBreakpointsToStorage(instance.localBreakpoints);
                        }
                        break;
                    case 'toggle-enable':
                        if (instance.localBreakpoints && instance.localBreakpoints[file] && instance.localBreakpoints[file][line]) {
                            instance.localBreakpoints[file][line].enabled = !instance.localBreakpoints[file][line].enabled;
                            this.saveBreakpointsToStorage(instance.localBreakpoints);
                        }
                        break;
                }
            }

            switch (action) {
                case 'disable-all':
                    this.disableAllBreakpoints(instance);
                    break;
                case 'clear-all':
                    this.clearAllBreakpoints(instance);
                    break;
            }

            this.updateBreakpointMarkers(instance);
        },

        disableAllBreakpoints: function(instance) {
            if (instance.localBreakpoints) {
                for (var file in instance.localBreakpoints) {
                    for (var line in instance.localBreakpoints[file]) {
                        instance.localBreakpoints[file][line].enabled = false;
                    }
                }
                this.saveBreakpointsToStorage(instance.localBreakpoints);
            }
        },

        clearAllBreakpoints: function(instance) {
            instance.localBreakpoints = {};
            this.saveBreakpointsToStorage(instance.localBreakpoints);
        },

        showConditionDialog: function(instance, file, line) {
            var self = this;
            var bp = instance.debugger ? ZatoDebuggerCore.getBreakpoint(instance.debugger, file, line) : null;
            var currentCondition = bp ? bp.condition || '' : '';

            var overlay = document.createElement('div');
            overlay.className = 'zato-debugger-condition-overlay';

            var dialog = document.createElement('div');
            dialog.className = 'zato-debugger-condition-dialog';

            var title = document.createElement('div');
            title.className = 'zato-debugger-condition-title';
            title.textContent = 'Breakpoint condition';

            var input = document.createElement('input');
            input.type = 'text';
            input.className = 'zato-debugger-condition-input';
            input.placeholder = 'Enter condition (e.g., x > 5)';
            input.value = currentCondition;

            var buttons = document.createElement('div');
            buttons.className = 'zato-debugger-condition-buttons';

            var cancelBtn = document.createElement('button');
            cancelBtn.className = 'zato-debugger-condition-button zato-debugger-condition-button-secondary';
            cancelBtn.textContent = 'Cancel';

            var okBtn = document.createElement('button');
            okBtn.className = 'zato-debugger-condition-button zato-debugger-condition-button-primary';
            okBtn.textContent = 'OK';

            buttons.appendChild(cancelBtn);
            buttons.appendChild(okBtn);

            dialog.appendChild(title);
            dialog.appendChild(input);
            dialog.appendChild(buttons);
            overlay.appendChild(dialog);
            document.body.appendChild(overlay);

            input.focus();

            var close = function() {
                overlay.remove();
            };

            cancelBtn.addEventListener('click', close);

            okBtn.addEventListener('click', function() {
                var condition = input.value.trim();
                if (instance.debugger) {
                    if (bp) {
                        bp.condition = condition || null;
                        if (ZatoDebuggerCore.isDebugging(instance.debugger)) {
                            ZatoDebuggerProtocol.setBreakpoints(
                                instance.debugger,
                                file,
                                ZatoDebuggerCore.getBreakpointsForFile(instance.debugger, file)
                            );
                        }
                    } else {
                        ZatoDebuggerCore.addBreakpoint(instance.debugger, file, line, condition || null);
                    }
                    self.updateBreakpointMarkers(instance);
                }
                close();
            });

            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    okBtn.click();
                } else if (e.key === 'Escape') {
                    close();
                }
            });
        },

        getCurrentFile: function(instance) {
            if (instance.options.getFilename) {
                return instance.options.getFilename();
            }
            return 'untitled.py';
        },

        updateBreakpointMarkers: function(instance) {
            var editor = instance.editor;
            var session = editor.session;
            var file = this.getCurrentFile(instance);
            var breakpoints = [];

            if (instance.debugger) {
                breakpoints = ZatoDebuggerCore.getBreakpointsForFile(instance.debugger, file);
            } else if (instance.localBreakpoints && instance.localBreakpoints[file]) {
                for (var line in instance.localBreakpoints[file]) {
                    breakpoints.push(instance.localBreakpoints[file][line]);
                }
            }

            session.clearBreakpoints();

            for (var i = 0; i < breakpoints.length; i++) {
                var bp = breakpoints[i];
                var row = bp.line - 1;
                var bpClass = 'ace_breakpoint';
                if (!bp.enabled) {
                    bpClass = 'ace_breakpoint ace_breakpoint-disabled';
                } else if (bp.condition) {
                    bpClass = 'ace_breakpoint ace_breakpoint-conditional';
                }
                session.setBreakpoint(row, bpClass);
            }
        },

        updateCurrentLineMarker: function(instance) {
            var editor = instance.editor;
            var session = editor.session;

            if (instance.currentLineMarkerId !== null) {
                session.removeMarker(instance.currentLineMarkerId);
                instance.currentLineMarkerId = null;
            }

            if (!instance.debugger) {
                return;
            }

            var dbg = instance.debugger;
            if (!ZatoDebuggerCore.isPaused(dbg)) {
                return;
            }

            var currentFile = this.getCurrentFile(instance);
            if (dbg.currentFile !== currentFile) {
                return;
            }

            var line = dbg.currentLine;
            if (!line) {
                return;
            }

            var row = line - 1;
            var Range = ace.require('ace/range').Range;
            var range = new Range(row, 0, row, 1);

            instance.currentLineMarkerId = session.addMarker(range, 'zato-debugger-current-line', 'fullLine', true);

            editor.scrollToLine(row, true, true);
        },

        applyStyles: function(instance) {
            console.log('[Gutter] applyStyles: START');
            if (document.getElementById('zato-debugger-gutter-styles')) {
                console.log('[Gutter] applyStyles: styles already exist, skipping');
                return;
            }

            console.log('[Gutter] applyStyles: creating new style element');
            var style = document.createElement('style');
            style.id = 'zato-debugger-gutter-styles';
            style.textContent = this.getGutterStyles();
            document.head.appendChild(style);
            console.log('[Gutter] applyStyles: END');
        },

        getGutterStyles: function() {
            var css = '';

            var redCircle = 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12"><circle cx="6" cy="6" r="5" fill="#e51400"/></svg>');
            var grayCircle = 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12"><circle cx="6" cy="6" r="5" fill="#555555"/></svg>');
            var orangeCircle = 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12"><circle cx="6" cy="6" r="5" fill="#f0a000"/></svg>');

            css += '.ace_gutter-cell.ace_breakpoint {';
            css += '  background-image: url("' + redCircle + '");';
            css += '  background-repeat: no-repeat;';
            css += '  background-position: 2px center;';
            css += '}';

            css += '.ace_gutter-cell.ace_breakpoint-disabled {';
            css += '  background-image: url("' + grayCircle + '");';
            css += '  background-repeat: no-repeat;';
            css += '  background-position: 2px center;';
            css += '}';

            css += '.ace_gutter-cell.ace_breakpoint-conditional {';
            css += '  background-image: url("' + orangeCircle + '");';
            css += '  background-repeat: no-repeat;';
            css += '  background-position: 2px center;';
            css += '}';

            css += '.zato-debugger-current-line {';
            css += '  position: absolute;';
            css += '  background: rgba(255, 238, 0, 0.2);';
            css += '  border-left: 2px solid #ffee00;';
            css += '}';

            return css;
        },

        clearAllMarkers: function(instance) {
            var editor = instance.editor;
            var session = editor.session;

            for (var row in instance.breakpointDecorations) {
                session.removeGutterDecoration(parseInt(row, 10), instance.breakpointDecorations[row]);
            }
            instance.breakpointDecorations = {};

            if (instance.currentLineMarkerId !== null) {
                session.removeMarker(instance.currentLineMarkerId);
                instance.currentLineMarkerId = null;
            }
        }
    };

    window.ZatoDebuggerGutter = ZatoDebuggerGutter;

})();
