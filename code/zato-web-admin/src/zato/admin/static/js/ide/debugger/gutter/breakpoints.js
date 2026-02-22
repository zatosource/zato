(function() {
    'use strict';

    var G = window.ZatoDebuggerGutter;

    G.handleGutterClick = function(instance, event) {
        console.log('[Gutter] handleGutterClick: START');
        console.log('[Gutter] handleGutterClick: event.target.tagName=' + event.target.tagName);
        console.log('[Gutter] handleGutterClick: event.target.className=' + event.target.className);
        console.log('[Gutter] handleGutterClick: event.clientY=' + event.clientY);

        var editor = instance.editor;

        var screenPos = editor.renderer.pixelToScreenCoordinates(event.clientX, event.clientY);
        var row = editor.session.screenToDocumentRow(screenPos.row, screenPos.column);

        console.log('[Gutter] handleGutterClick: screenPos.row=' + screenPos.row);
        console.log('[Gutter] handleGutterClick: row=' + row);

        if (isNaN(row)) {
            console.log('[Gutter] handleGutterClick: row is NaN, returning');
            return;
        }

        var line = row + 1;
        var file = this.getCurrentFile(instance);
        var lineText = editor.session.getLine(row);
        var lineType = this.getLineType(lineText);
        console.log('[Gutter] handleGutterClick: line=' + line + ' file=' + file);
        console.log('[Gutter] handleGutterClick: lineText="' + lineText + '"');
        console.log('[Gutter] handleGutterClick: lineType=' + lineType);
        console.log('[Gutter] handleGutterClick: instance.debugger=' + (instance.debugger ? 'exists' : 'null'));

        if (instance.debugger) {
            console.log('[Gutter] handleGutterClick: calling ZatoDebuggerCore.toggleBreakpoint');
            var bp = ZatoDebuggerCore.toggleBreakpoint(instance.debugger, file, line);
            console.log('[Gutter] handleGutterClick: toggleBreakpoint returned=' + JSON.stringify(bp));
            this.updateBreakpointMarkers(instance);
        } else {
            console.log('[Gutter] handleGutterClick: calling toggleLocalBreakpoint');
            this.toggleLocalBreakpoint(instance, file, line, lineType);
        }
        console.log('[Gutter] handleGutterClick: END');
    };

    G.toggleLocalBreakpoint = function(instance, file, line, lineType) {
        console.log('[Gutter] toggleLocalBreakpoint: file=' + file + ' line=' + line + ' lineType=' + lineType);
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
            var targetLine = line;
            if (!this.isBreakableLine(lineType)) {
                console.log('[Gutter] toggleLocalBreakpoint: line ' + line + ' is not breakable (type=' + lineType + '), finding next breakable line');
                targetLine = this.findFirstBreakableLine(instance, line);
                if (targetLine === null) {
                    console.log('[Gutter] toggleLocalBreakpoint: no breakable line found after line ' + line);
                    return;
                }
                console.log('[Gutter] toggleLocalBreakpoint: found next breakable line at ' + targetLine);
                if (instance.localBreakpoints[file] && instance.localBreakpoints[file][targetLine]) {
                    console.log('[Gutter] toggleLocalBreakpoint: target line ' + targetLine + ' already has breakpoint, doing nothing');
                    return;
                }
            }
            console.log('[Gutter] toggleLocalBreakpoint: adding breakpoint at line ' + targetLine);
            instance.localBreakpoints[file][targetLine] = { line: targetLine, enabled: true };
        }
        console.log('[Gutter] toggleLocalBreakpoint: localBreakpoints[' + file + ']=' + JSON.stringify(instance.localBreakpoints[file]));
        this.saveBreakpointsToStorage(instance.localBreakpoints);
        this.updateBreakpointMarkers(instance);
    };

    G.loadBreakpointsFromStorage = function() {
        try {
            var stored = localStorage.getItem('zato-ide-breakpoints');
            if (stored) {
                return JSON.parse(stored);
            }
        } catch (e) {
            console.error('[DebuggerGutter] Failed to load breakpoints from storage:', e);
        }
        return {};
    };

    G.saveBreakpointsToStorage = function(breakpoints) {
        try {
            localStorage.setItem('zato-ide-breakpoints', JSON.stringify(breakpoints));
        } catch (e) {
            console.error('[DebuggerGutter] Failed to save breakpoints to storage:', e);
        }
    };

    G.handleGutterContextMenu = function(instance, event) {
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
    };

    G.showBreakpointContextMenu = function(instance, x, y, file, line) {
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
    };

    G.handleBreakpointAction = function(instance, action, file, line) {
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
    };

    G.disableAllBreakpoints = function(instance) {
        if (instance.localBreakpoints) {
            for (var file in instance.localBreakpoints) {
                for (var line in instance.localBreakpoints[file]) {
                    instance.localBreakpoints[file][line].enabled = false;
                }
            }
            this.saveBreakpointsToStorage(instance.localBreakpoints);
        }
    };

    G.clearAllBreakpoints = function(instance) {
        instance.localBreakpoints = {};
        this.saveBreakpointsToStorage(instance.localBreakpoints);
    };

    G.showConditionDialog = function(instance, file, line) {
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
    };

    G.getCurrentFile = function(instance) {
        if (instance.options.getFilePath) {
            return instance.options.getFilePath();
        }
        if (instance.options.getFilename) {
            return instance.options.getFilename();
        }
        return null;
    };

    G.getLineType = function(lineText) {
        var trimmed = lineText.trim();
        if (trimmed === '') {
            return 'empty';
        }
        if (trimmed.startsWith('#')) {
            return 'comment';
        }
        if (trimmed.startsWith('"""') || trimmed.startsWith("'''")) {
            return 'docstring';
        }
        if (trimmed.startsWith('def ') || trimmed.startsWith('class ') || trimmed.startsWith('async def ')) {
            return 'definition';
        }
        if (trimmed.startsWith('import ') || trimmed.startsWith('from ')) {
            return 'import';
        }
        if (trimmed.startsWith('@')) {
            return 'decorator';
        }
        if (trimmed.startsWith('if ') || trimmed.startsWith('elif ') || trimmed === 'else:' || trimmed.startsWith('else:')) {
            return 'block_header';
        }
        if (trimmed.startsWith('for ') || trimmed.startsWith('while ') || trimmed.startsWith('async for ')) {
            return 'block_header';
        }
        if (trimmed === 'try:' || trimmed.startsWith('except ') || trimmed.startsWith('except:') || trimmed === 'finally:' || trimmed.startsWith('finally:')) {
            return 'block_header';
        }
        if (trimmed.startsWith('with ') || trimmed.startsWith('async with ')) {
            return 'block_header';
        }
        return 'code';
    };

    G.isBreakableLine = function(lineType) {
        return lineType === 'code' || lineType === 'import';
    };

    G.findFirstBreakableLine = function(instance, startLine) {
        var editor = instance.editor;
        var session = editor.session;
        var totalLines = session.getLength();

        for (var line = startLine; line <= totalLines; line++) {
            var row = line - 1;
            var lineText = session.getLine(row);
            var lineType = this.getLineType(lineText);

            if (this.isBreakableLine(lineType)) {
                return line;
            }
        }
        return null;
    };

})();
