(function() {
    'use strict';

    var UI = window.ZatoDebuggerUI;

    UI.updateToolbarState = function(instance) {
        var dbg = instance.debugger;
        var continueBtn = instance.elements.continueBtn;

        if (!instance.isConnected) {
            var enableContinue = !instance.isConnecting;
            UI.setButtonEnabled(continueBtn, enableContinue);
            UI.setButtonEnabled(instance.elements.pauseBtn, false);
            UI.setButtonEnabled(instance.elements.stepOverBtn, false);
            UI.setButtonEnabled(instance.elements.stepIntoBtn, false);
            UI.setButtonEnabled(instance.elements.stepOutBtn, false);
            UI.setButtonEnabled(instance.elements.restartBtn, false);
            UI.setButtonEnabled(instance.elements.stopBtn, false);
            if (continueBtn) {
                continueBtn.setAttribute('data-tooltip', 'Start debugging (F5)');
            }
            return;
        }

        if (!dbg || typeof ZatoDebuggerCore === 'undefined') {
            UI.setButtonEnabled(continueBtn, true);
            UI.setButtonEnabled(instance.elements.pauseBtn, false);
            UI.setButtonEnabled(instance.elements.stepOverBtn, false);
            UI.setButtonEnabled(instance.elements.stepIntoBtn, false);
            UI.setButtonEnabled(instance.elements.stepOutBtn, false);
            UI.setButtonEnabled(instance.elements.restartBtn, false);
            UI.setButtonEnabled(instance.elements.stopBtn, false);
            if (continueBtn) {
                continueBtn.setAttribute('data-tooltip', 'Start (F5)');
            }
            return;
        }

        var state = ZatoDebuggerCore.getState(dbg);
        var isPaused = state === ZatoDebuggerCore.DebugState.PAUSED;
        var isRunning = state === ZatoDebuggerCore.DebugState.RUNNING;
        var isDebugging = ZatoDebuggerCore.isDebugging(dbg);

        UI.setButtonEnabled(continueBtn, !isDebugging || isPaused);
        UI.setButtonEnabled(instance.elements.pauseBtn, isRunning);
        UI.setButtonEnabled(instance.elements.stepOverBtn, isPaused);
        UI.setButtonEnabled(instance.elements.stepIntoBtn, isPaused);
        UI.setButtonEnabled(instance.elements.stepOutBtn, isPaused);
        UI.setButtonEnabled(instance.elements.restartBtn, isDebugging);
        UI.setButtonEnabled(instance.elements.stopBtn, isDebugging);

        if (continueBtn) {
            if (isDebugging) {
                continueBtn.setAttribute('data-tooltip', 'Continue (F5)');
            } else {
                continueBtn.setAttribute('data-tooltip', 'Start (F5)');
            }
        }
    };

    UI.setButtonEnabled = function(button, enabled) {
        if (button) {
            button.disabled = !enabled;
            button.classList.toggle('disabled', !enabled);
        }
    };

    UI.updateCallStack = function(instance, frames) {
        var list = instance.elements.callStackList;
        if (!list) {
            return;
        }

        if (!frames || frames.length === 0) {
            list.innerHTML = '<div class="zato-debugger-empty">No call stack</div>';
            return;
        }

        var html = '';
        for (var i = 0; i < frames.length; i++) {
            var frame = frames[i];
            var isActive = i === 0;
            var source = frame.source ? frame.source.name : 'unknown';
            html += '<div class="zato-debugger-frame-item' + (isActive ? ' active' : '') + '" data-frame-id="' + frame.id + '">';
            html += '<span class="zato-debugger-frame-name">' + UI.escapeHtml(frame.name) + '</span>';
            html += '<span class="zato-debugger-frame-location">' + UI.escapeHtml(source) + ':' + frame.line + '</span>';
            html += '</div>';
        }
        list.innerHTML = html;
    };

    UI.updateVariables = function(instance, scopeRef, variables) {
        var list = instance.elements.variablesList;
        if (!list) {
            return;
        }

        if (!variables || variables.length === 0) {
            list.innerHTML = '<div class="zato-debugger-empty">No variables</div>';
            return;
        }

        var html = UI.renderVariablesList(variables, 0);
        list.innerHTML = html;
    };

    UI.renderVariablesList = function(variables, depth) {
        var html = '';
        for (var i = 0; i < variables.length; i++) {
            var v = variables[i];
            var hasChildren = v.variablesReference && v.variablesReference > 0;
            var indent = depth * 16;
            html += '<div class="zato-debugger-variable-item' + (hasChildren ? ' expandable' : '') + '" ';
            html += 'data-ref="' + (v.variablesReference || 0) + '" style="padding-left: ' + indent + 'px;">';
            if (hasChildren) {
                html += '<span class="zato-debugger-variable-toggle">' + UI.getChevronIcon() + '</span>';
            }
            html += '<span class="zato-debugger-variable-name">' + UI.escapeHtml(v.name) + '</span>';
            html += '<span class="zato-debugger-variable-separator">:</span>';
            html += '<span class="zato-debugger-variable-value">' + UI.escapeHtml(v.value) + '</span>';
            if (v.type) {
                html += '<span class="zato-debugger-variable-type">' + UI.escapeHtml(v.type) + '</span>';
            }
            html += '</div>';
        }
        return html;
    };

    UI.toggleVariable = function(instance, varItem) {
        varItem.classList.toggle('expanded');
    };

    UI.updateWatches = function(instance) {
        var list = instance.elements.watchesList;
        if (!list) {
            return;
        }

        var watches = instance.debugger ? instance.debugger.watches : [];
        if (!watches || watches.length === 0) {
            list.innerHTML = '<div class="zato-debugger-empty">No watch expressions</div>';
            return;
        }

        var html = '';
        for (var i = 0; i < watches.length; i++) {
            var w = watches[i];
            html += '<div class="zato-debugger-watch-item" data-watch-id="' + w.id + '">';
            html += '<span class="zato-debugger-watch-expr">' + UI.escapeHtml(w.expression) + '</span>';
            html += '<span class="zato-debugger-watch-separator">:</span>';
            html += '<span class="zato-debugger-watch-value">' + UI.highlightPythonValue(w.value || '<not available>') + '</span>';
            html += '<button class="zato-debugger-watch-remove" data-action="remove-watch" data-watch-id="' + w.id + '">';
            html += UI.getCloseIcon();
            html += '</button>';
            html += '</div>';
        }
        list.innerHTML = html;
    };

    UI.saveWatches = function(instance) {
        var watches = instance.debugger ? instance.debugger.watches : [];
        var expressions = [];
        if (watches && watches.length > 0) {
            for (var i = 0; i < watches.length; i++) {
                expressions.push(watches[i].expression);
            }
        }
        UI.saveState('watches', expressions);
    };

    UI.restoreWatches = function(instance) {
        var expressions = UI.loadState('watches');
        if (!expressions || !Array.isArray(expressions) || expressions.length === 0) {
            return;
        }
        if (!instance.debugger || typeof ZatoDebuggerCore === 'undefined') {
            return;
        }
        for (var i = 0; i < expressions.length; i++) {
            ZatoDebuggerCore.addWatch(instance.debugger, expressions[i]);
        }
        UI.updateWatches(instance);
    };

    UI.updateBreakpoints = function(instance) {
        console.log('[DebuggerUI] updateBreakpoints: START');
        var list = instance.elements.breakpointsList;
        if (!list) {
            console.log('[DebuggerUI] updateBreakpoints: no breakpointsList element found');
            return;
        }

        console.log('[DebuggerUI] updateBreakpoints: loading from localStorage');
        var breakpoints = UI.loadBreakpointsFromStorage();
        console.log('[DebuggerUI] updateBreakpoints: loaded ' + breakpoints.length + ' breakpoints');
        console.log('[DebuggerUI] updateBreakpoints: breakpoints=' + JSON.stringify(breakpoints));
        if (!breakpoints || breakpoints.length === 0) {
            console.log('[DebuggerUI] updateBreakpoints: no breakpoints, showing empty message');
            list.innerHTML = '<div class="zato-debugger-empty">No breakpoints</div>';
            return;
        }

        console.log('[DebuggerUI] updateBreakpoints: rendering ' + breakpoints.length + ' items to list');
        var html = '';
        for (var i = 0; i < breakpoints.length; i++) {
            var bp = breakpoints[i];
            var filename = bp.file.split('/').pop();
            var enabledClass = bp.enabled ? '' : ' disabled';
            console.log('[DebuggerUI] updateBreakpoints: rendering item ' + i + ': file=' + filename + ' line=' + bp.line + ' enabled=' + bp.enabled);
            html += '<div class="zato-debugger-breakpoint-item' + enabledClass + '" data-file="' + UI.escapeHtml(bp.file) + '" data-line="' + bp.line + '" data-enabled="' + (bp.enabled ? 'true' : 'false') + '">';
            html += '<span class="zato-debugger-breakpoint-icon' + enabledClass + '" data-action="toggle-enabled">' + UI.getBreakpointIcon() + '</span>';
            html += '<span class="zato-debugger-breakpoint-file">' + UI.escapeHtml(filename) + '</span>';
            html += '<button class="zato-debugger-breakpoint-goto" data-file="' + UI.escapeHtml(bp.file) + '" data-line="' + bp.line + '">Go to file</button>';
            html += '<span class="zato-debugger-breakpoint-line">:' + bp.line + '</span>';
            if (bp.condition) {
                html += '<span class="zato-debugger-breakpoint-condition">' + UI.escapeHtml(bp.condition) + '</span>';
            }
            html += '<button class="zato-debugger-breakpoint-remove" data-action="remove-breakpoint" data-file="' + UI.escapeHtml(bp.file) + '" data-line="' + bp.line + '">';
            html += UI.getTrashIcon();
            html += '</button>';
            html += '</div>';
        }
        console.log('[DebuggerUI] updateBreakpoints: setting list.innerHTML, html.length=' + html.length);
        list.innerHTML = html;
        console.log('[DebuggerUI] updateBreakpoints: list updated, childElementCount=' + list.childElementCount);
    };

    UI.selectFrame = function(instance, frameId) {
        if (instance.debugger) {
            ZatoDebuggerCore.selectFrame(instance.debugger, frameId);
        }

        var items = instance.elements.callStackList.querySelectorAll('.zato-debugger-frame-item');
        for (var i = 0; i < items.length; i++) {
            var item = items[i];
            var id = parseInt(item.getAttribute('data-frame-id'), 10);
            item.classList.toggle('active', id === frameId);
        }
    };

    UI.jumpToBreakpoint = function(instance, file, line) {
        if (instance.onJumpToLine) {
            instance.onJumpToLine(file, line);
        }
    };

    UI.highlightCurrentLine = function(instance) {
        if (instance.onHighlightLine && instance.debugger) {
            var dbg = instance.debugger;
            if (dbg.currentFile && dbg.currentLine) {
                instance.onHighlightLine(dbg.currentFile, dbg.currentLine);
            }
        }
    };

    UI.escapeHtml = function(text) {
        if (text === null || text === undefined) {
            return '';
        }
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    };

    UI.loadBreakpointsFromStorage = function() {
        console.log('[DebuggerUI] loadBreakpointsFromStorage: reading localStorage');
        try {
            var stored = localStorage.getItem('zato-ide-breakpoints');
            console.log('[DebuggerUI] loadBreakpointsFromStorage: raw=' + stored);
            if (stored) {
                var data = JSON.parse(stored);
                var breakpoints = [];
                for (var file in data) {
                    for (var line in data[file]) {
                        var bp = data[file][line];
                        bp.file = file;
                        breakpoints.push(bp);
                    }
                }
                console.log('[DebuggerUI] loadBreakpointsFromStorage: parsed ' + breakpoints.length + ' breakpoints');
                return breakpoints;
            }
        } catch (e) {
            console.error('[DebuggerUI] Failed to load breakpoints from storage:', e);
        }
        console.log('[DebuggerUI] loadBreakpointsFromStorage: returning empty array');
        return [];
    };

    UI.saveBreakpointsToStorage = function(breakpoints) {
        try {
            var data = {};
            for (var i = 0; i < breakpoints.length; i++) {
                var bp = breakpoints[i];
                var file = bp.file;
                if (!data[file]) {
                    data[file] = {};
                }
                data[file][bp.line] = bp;
            }
            localStorage.setItem('zato-ide-breakpoints', JSON.stringify(data));
        } catch (e) {
            console.error('[DebuggerUI] Failed to save breakpoints to storage:', e);
        }
    };

    UI.removeBreakpointFromStorage = function(file, line) {
        console.log('[DebuggerUI] removeBreakpointFromStorage: file=' + file + ' line=' + line);
        try {
            var stored = localStorage.getItem('zato-ide-breakpoints');
            console.log('[DebuggerUI] removeBreakpointFromStorage: before=' + stored);
            if (stored) {
                var data = JSON.parse(stored);
                if (data[file] && data[file][line]) {
                    delete data[file][line];
                    if (Object.keys(data[file]).length === 0) {
                        delete data[file];
                    }
                    localStorage.setItem('zato-ide-breakpoints', JSON.stringify(data));
                    console.log('[DebuggerUI] removeBreakpointFromStorage: after=' + localStorage.getItem('zato-ide-breakpoints'));
                } else {
                    console.log('[DebuggerUI] removeBreakpointFromStorage: breakpoint not found in storage');
                }
            } else {
                console.log('[DebuggerUI] removeBreakpointFromStorage: no breakpoints in storage');
            }
        } catch (e) {
            console.error('[DebuggerUI] Failed to remove breakpoint from storage:', e);
        }
    };

    UI.setBreakpointEnabledInStorage = function(file, line, enabled) {
        try {
            var stored = localStorage.getItem('zato-ide-breakpoints');
            if (stored) {
                var data = JSON.parse(stored);
                if (data[file] && data[file][line]) {
                    data[file][line].enabled = enabled;
                    localStorage.setItem('zato-ide-breakpoints', JSON.stringify(data));
                }
            }
        } catch (e) {
            console.error('[DebuggerUI] Failed to update breakpoint in storage:', e);
        }
    };

})();
