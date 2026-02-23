(function() {
    'use strict';

    var G = window.ZatoDebuggerGutter;

    G.updateBreakpointMarkers = function(instance) {
        console.log('[Gutter] updateBreakpointMarkers: START');
        var editor = instance.editor;
        var session = editor.session;
        var file = this.getCurrentFile(instance);
        console.log('[Gutter] updateBreakpointMarkers: file=' + file);
        if (!file) {
            console.log('[Gutter] updateBreakpointMarkers: no file, returning');
            return;
        }
        var breakpoints = [];

        if (!instance.localBreakpoints) {
            console.log('[Gutter] updateBreakpointMarkers: loading breakpoints from storage');
            instance.localBreakpoints = this.loadBreakpointsFromStorage();
            console.log('[Gutter] updateBreakpointMarkers: loaded=' + JSON.stringify(instance.localBreakpoints));
        }

        if (instance.debugger) {
            console.log('[Gutter] updateBreakpointMarkers: using debugger core');
            breakpoints = ZatoDebuggerCore.getBreakpointsForFile(instance.debugger, file);
        } else if (instance.localBreakpoints && instance.localBreakpoints[file]) {
            console.log('[Gutter] updateBreakpointMarkers: using localBreakpoints');
            for (var line in instance.localBreakpoints[file]) {
                breakpoints.push(instance.localBreakpoints[file][line]);
            }
        }
        console.log('[Gutter] updateBreakpointMarkers: breakpoints for file=' + JSON.stringify(breakpoints));

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
            console.log('[Gutter] updateBreakpointMarkers: setting breakpoint row=' + row + ' class=' + bpClass);
            session.setBreakpoint(row, bpClass);
            var gutterCells = editor.renderer.$gutterLayer.element.querySelectorAll('.ace_gutter-cell');
            console.log('[Gutter] updateBreakpointMarkers: gutterCells.length=' + gutterCells.length);
            if (gutterCells[row]) {
                console.log('[Gutter] updateBreakpointMarkers: gutterCells[' + row + '].className=' + gutterCells[row].className);
                var computedStyle = window.getComputedStyle(gutterCells[row]);
                console.log('[Gutter] updateBreakpointMarkers: background-image=' + computedStyle.backgroundImage);
                console.log('[Gutter] updateBreakpointMarkers: background-position=' + computedStyle.backgroundPosition);
                var beforeStyle = window.getComputedStyle(gutterCells[row], '::before');
                console.log('[Gutter] updateBreakpointMarkers: ::before left=' + beforeStyle.left + ' position=' + beforeStyle.position + ' content=' + beforeStyle.content);
            }
        }
    };

    G.updateCurrentLineMarker = function(instance) {
        console.log('[Gutter] updateCurrentLineMarker: START');
        var editor = instance.editor;
        var session = editor.session;

        if (instance.currentLineMarkerId !== null) {
            console.log('[Gutter] updateCurrentLineMarker: removing old marker');
            session.removeMarker(instance.currentLineMarkerId);
            instance.currentLineMarkerId = null;
        }

        if (instance.currentGutterRow !== undefined && instance.currentGutterRow !== null) {
            session.removeGutterDecoration(instance.currentGutterRow, 'ace_gutter-active-line');
            instance.currentGutterRow = null;
        }

        if (!instance.debugger) {
            console.log('[Gutter] updateCurrentLineMarker: no debugger, returning');
            return;
        }

        var dbg = instance.debugger;
        console.log('[Gutter] updateCurrentLineMarker: dbg.state=' + dbg.state);
        console.log('[Gutter] updateCurrentLineMarker: dbg.currentFile=' + dbg.currentFile);
        console.log('[Gutter] updateCurrentLineMarker: dbg.currentLine=' + dbg.currentLine);

        if (!ZatoDebuggerCore.isPaused(dbg)) {
            console.log('[Gutter] updateCurrentLineMarker: not paused, returning');
            return;
        }

        var currentFile = this.getCurrentFile(instance);
        console.log('[Gutter] updateCurrentLineMarker: currentFile=' + currentFile);
        if (dbg.currentFile !== currentFile) {
            console.log('[Gutter] updateCurrentLineMarker: file mismatch, returning');
            return;
        }

        var line = dbg.currentLine;
        if (!line) {
            console.log('[Gutter] updateCurrentLineMarker: no currentLine, returning');
            return;
        }

        var row = line - 1;
        var Range = ace.require('ace/range').Range;
        var range = new Range(row, 0, row, 1);

        console.log('[Gutter] updateCurrentLineMarker: adding marker at row=' + row);
        instance.currentLineMarkerId = session.addMarker(range, 'zato-debugger-current-line', 'fullLine', true);
        console.log('[Gutter] updateCurrentLineMarker: markerId=' + instance.currentLineMarkerId);

        session.addGutterDecoration(row, 'ace_gutter-active-line');
        instance.currentGutterRow = row;

        editor.scrollToLine(row, true, true);
    };

    G.clearAllMarkers = function(instance) {
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

        if (instance.currentGutterRow !== undefined && instance.currentGutterRow !== null) {
            session.removeGutterDecoration(instance.currentGutterRow, 'ace_gutter-active-line');
            instance.currentGutterRow = null;
        }
    };

    G.setupMutationObserver = function(instance) {
        console.log('[Gutter] setupMutationObserver: START');
        var editor = instance.editor;
        var gutterElement = editor.renderer.$gutterLayer.element;
        console.log('[Gutter] setupMutationObserver: gutterElement=' + (gutterElement ? 'exists' : 'null'));

        if (instance.mutationObserver) {
            console.log('[Gutter] setupMutationObserver: observer already exists, disconnecting');
            instance.mutationObserver.disconnect();
        }

        instance.mutationObserver = new MutationObserver(function(mutations) {
            for (var i = 0; i < mutations.length; i++) {
                var mutation = mutations[i];
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    var target = mutation.target;
                    if (target.classList.contains('ace_gutter-cell')) {
                        var oldValue = mutation.oldValue || '';
                        var newValue = target.className;
                        var hadBreakpoint = oldValue.indexOf('ace_breakpoint') !== -1;
                        var hasBreakpoint = newValue.indexOf('ace_breakpoint') !== -1;
                        if (hadBreakpoint && !hasBreakpoint) {
                            console.log('[Gutter] MutationObserver: breakpoint class REMOVED from cell');
                            console.log('[Gutter] MutationObserver: oldValue=' + oldValue);
                            console.log('[Gutter] MutationObserver: newValue=' + newValue);
                            console.log('[Gutter] MutationObserver: stack=' + new Error().stack);
                        }
                    }
                }
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    var target = mutation.target;
                    if (target.classList.contains('ace_gutter-cell') && target.classList.contains('ace_breakpoint')) {
                        console.log('[Gutter] MutationObserver: style changed on breakpoint cell');
                        console.log('[Gutter] MutationObserver: newStyle=' + target.getAttribute('style'));
                        console.log('[Gutter] MutationObserver: stack=' + new Error().stack);
                    }
                }
                if (mutation.type === 'childList') {
                    for (var j = 0; j < mutation.removedNodes.length; j++) {
                        var node = mutation.removedNodes[j];
                        if (node.nodeType === 1 && node.classList && node.classList.contains('ace_gutter-cell')) {
                            if (node.classList.contains('ace_breakpoint')) {
                                console.log('[Gutter] MutationObserver: breakpoint cell REMOVED from DOM');
                                console.log('[Gutter] MutationObserver: className=' + node.className);
                                console.log('[Gutter] MutationObserver: stack=' + new Error().stack);
                            }
                        }
                    }
                }
            }
        });

        instance.mutationObserver.observe(gutterElement, {
            attributes: true,
            attributeOldValue: true,
            childList: true,
            subtree: true
        });
        console.log('[Gutter] setupMutationObserver: observer started');
    };

})();
