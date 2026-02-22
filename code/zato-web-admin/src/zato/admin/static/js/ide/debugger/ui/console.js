(function() {
    'use strict';

    var UI = window.ZatoDebuggerUI;

    UI.evaluateInConsole = function(instance, expression) {
        UI.appendConsoleOutput(instance, 'input', '> ' + expression);

        if (!instance.debugger || typeof ZatoDebuggerCore === 'undefined') {
            UI.appendConsoleOutput(instance, 'error', 'Debugger not running');
            return;
        }
        if (!ZatoDebuggerCore.isDebugging(instance.debugger)) {
            UI.appendConsoleOutput(instance, 'error', 'Debugger not running');
            return;
        }
        if (!ZatoDebuggerCore.isPaused(instance.debugger)) {
            UI.appendConsoleOutput(instance, 'error', 'Debugger not paused');
            return;
        }
        var frame = instance.debugger.currentFrame;
        if (frame && typeof ZatoDebuggerProtocol !== 'undefined') {
            ZatoDebuggerProtocol.evaluate(instance.debugger, expression, frame.id, function(result) {
                UI.appendConsoleOutput(instance, 'output', result.result);
            });
        }
    };

    UI.appendConsoleOutput = function(instance, category, text) {
        var output = instance.elements.consoleOutput;
        if (!output) {
            return;
        }

        var line = document.createElement('div');
        line.className = 'zato-debugger-console-line zato-debugger-console-' + category;
        if (category === 'output') {
            line.innerHTML = UI.highlightPythonValue(text);
        } else {
            line.textContent = text;
        }
        output.appendChild(line);
        output.scrollTop = output.scrollHeight;
        UI.saveConsoleOutput(instance);
    };

    UI.saveConsoleOutput = function(instance) {
        var output = instance.elements.consoleOutput;
        if (!output) {
            return;
        }
        var lines = output.querySelectorAll('.zato-debugger-console-line');
        var data = [];
        for (var i = 0; i < lines.length && i < 200; i++) {
            var line = lines[i];
            var category = 'output';
            if (line.classList.contains('zato-debugger-console-input')) {
                category = 'input';
            } else if (line.classList.contains('zato-debugger-console-error')) {
                category = 'error';
            }
            data.push({ category: category, text: line.textContent });
        }
        UI.saveState('console-output', data);
    };

    UI.restoreConsoleOutput = function(instance) {
        var data = UI.loadState('console-output');
        if (!data || !Array.isArray(data)) {
            return;
        }
        var output = instance.elements.consoleOutput;
        if (!output) {
            return;
        }
        for (var i = 0; i < data.length; i++) {
            var item = data[i];
            var line = document.createElement('div');
            line.className = 'zato-debugger-console-line zato-debugger-console-' + item.category;
            if (item.category === 'output') {
                line.innerHTML = UI.highlightPythonValue(item.text);
            } else {
                line.textContent = item.text;
            }
            output.appendChild(line);
        }
    };

    UI.highlightPythonValue = function(text) {
        if (text === null || text === undefined) {
            return '';
        }
        var escaped = UI.escapeHtml(String(text));
        escaped = escaped.replace(/\b(True|False|None)\b/g, '<span class="zato-debugger-hl-keyword">$1</span>');
        escaped = escaped.replace(/\b(\d+\.?\d*)\b/g, '<span class="zato-debugger-hl-number">$1</span>');
        escaped = escaped.replace(/('[^']*'|"[^"]*")/g, '<span class="zato-debugger-hl-string">$1</span>');
        escaped = escaped.replace(/&lt;([^&]+)&gt;/g, '<span class="zato-debugger-hl-type">&lt;$1&gt;</span>');
        return escaped;
    };

})();
