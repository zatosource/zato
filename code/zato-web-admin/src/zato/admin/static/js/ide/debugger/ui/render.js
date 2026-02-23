(function() {
    'use strict';

    var UI = window.ZatoDebuggerUI;

    UI.render = function(instance) {
        var html = '';
        html += '<div class="zato-debugger-container zato-debugger-theme-' + instance.options.theme + '">';
        html += UI.renderToolbar(instance);
        html += '<div class="zato-debugger-panels">';
        
        var panelOrder = UI.loadPanelOrder();
        var panelRenderers = {
            'callStack': UI.renderCallStackPanel,
            'variables': UI.renderVariablesPanel,
            'watches': UI.renderWatchesPanel,
            'breakpoints': UI.renderBreakpointsPanel,
            'console': UI.renderConsolePanel
        };
        for (var i = 0; i < panelOrder.length; i++) {
            var panelId = panelOrder[i];
            if (panelRenderers[panelId]) {
                html += panelRenderers[panelId](instance);
            }
        }
        
        html += '</div>';
        html += '</div>';

        instance.container.innerHTML = html;
        UI.cacheElements(instance);
        UI.applyLastPanelExpand(instance);
    };
    
    UI.loadPanelOrder = function() {
        var defaultOrder = ['callStack', 'variables', 'watches', 'breakpoints', 'console'];
        try {
            var stored = localStorage.getItem('zato-debugger-panel-order');
            if (stored) {
                var order = JSON.parse(stored);
                if (Array.isArray(order) && order.length === 5) {
                    return order;
                }
            }
        } catch (e) {}
        return defaultOrder;
    };
    
    UI.applyLastPanelExpand = function(instance) {
        var panelsContainer = instance.container.querySelector('.zato-debugger-panels');
        if (!panelsContainer) {
            return;
        }
        var panels = panelsContainer.querySelectorAll('.zato-debugger-panel[data-panel-id]');
        for (var i = 0; i < panels.length; i++) {
            panels[i].classList.remove('expand');
        }
        if (panels.length > 0) {
            panels[panels.length - 1].classList.add('expand');
        }
    };
    
    UI.savePanelOrder = function(order) {
        try {
            localStorage.setItem('zato-debugger-panel-order', JSON.stringify(order));
        } catch (e) {}
    };

    UI.cacheElements = function(instance) {
        var container = instance.container;
        instance.elements = {
            toolbar: container.querySelector('.zato-debugger-toolbar'),
            continueBtn: container.querySelector('[data-action="continue"]'),
            pauseBtn: container.querySelector('[data-action="pause"]'),
            stepOverBtn: container.querySelector('[data-action="step-over"]'),
            stepIntoBtn: container.querySelector('[data-action="step-into"]'),
            stepOutBtn: container.querySelector('[data-action="step-out"]'),
            restartBtn: container.querySelector('[data-action="restart"]'),
            stopBtn: container.querySelector('[data-action="stop"]'),
            callStackPanel: container.querySelector('.zato-debugger-callstack'),
            callStackList: container.querySelector('.zato-debugger-callstack-list'),
            variablesPanel: container.querySelector('.zato-debugger-variables'),
            variablesList: container.querySelector('.zato-debugger-variables-list'),
            watchesPanel: container.querySelector('.zato-debugger-watches'),
            watchesList: container.querySelector('.zato-debugger-watches-list'),
            watchInput: container.querySelector('.zato-debugger-watch-input'),
            breakpointsPanel: container.querySelector('.zato-debugger-breakpoints'),
            breakpointsList: container.querySelector('.zato-debugger-breakpoints-list'),
            consolePanel: container.querySelector('.zato-debugger-console'),
            consoleOutput: container.querySelector('.zato-debugger-console-output'),
            consoleInput: container.querySelector('.zato-debugger-console-input')
        };
    };

    UI.renderToolbar = function(instance) {
        var html = '';
        html += '<div class="zato-debugger-toolbar">';
        html += '<div class="zato-debugger-toolbar-group">';
        html += UI.renderToolbarButton('continue', 'Continue', 'F5', UI.getContinueIcon());
        html += UI.renderToolbarButton('pause', 'Pause', 'F6', UI.getPauseIcon());
        html += '</div>';
        html += '<div class="zato-debugger-toolbar-separator"></div>';
        html += '<div class="zato-debugger-toolbar-group">';
        html += UI.renderToolbarButton('step-over', 'Step over', 'F10', UI.getStepOverIcon());
        html += UI.renderToolbarButton('step-into', 'Step into', 'F11', UI.getStepIntoIcon());
        html += UI.renderToolbarButton('step-out', 'Step out', 'Shift+F11', UI.getStepOutIcon());
        html += '</div>';
        html += '<div class="zato-debugger-toolbar-separator"></div>';
        html += '<div class="zato-debugger-toolbar-group">';
        html += UI.renderToolbarButton('restart', 'Restart', 'Ctrl+Shift+F5', UI.getRestartIcon());
        html += UI.renderToolbarButton('stop', 'Stop', 'Shift+F5', UI.getStopIcon());
        html += '</div>';
        html += '</div>';
        return html;
    };

    UI.renderToolbarButton = function(action, title, shortcut, iconPath) {
        var tooltip = title + ' (' + shortcut + ')';
        var iconHtml = iconPath.startsWith('<') ? iconPath : '<img src="' + iconPath + '" alt="' + title + '" class="zato-debugger-toolbar-icon">';
        return '<button class="zato-debugger-toolbar-button" data-action="' + action + '" data-tooltip="' + tooltip + '">' +
               iconHtml + '</button>';
    };

    UI.renderCallStackPanel = function(instance) {
        var html = '';
        html += '<div class="zato-debugger-panel zato-debugger-callstack empty" data-panel-id="callStack" draggable="true">';
        html += '<div class="zato-debugger-panel-header" data-panel="callStack">';
        html += '<span class="zato-debugger-panel-toggle">' + UI.getChevronIcon() + '</span>';
        html += '<span class="zato-debugger-panel-title">Call stack</span>';
        html += '<button class="zato-debugger-copy-btn" data-copy="callstack" data-tooltip="Copy to clipboard">Copy</button>';
        html += '</div>';
        html += '<div class="zato-debugger-panel-content">';
        html += '<div class="zato-debugger-callstack-list"><div class="zato-debugger-empty">No call stack</div></div>';
        html += '</div>';
        html += '</div>';
        return html;
    };

    UI.renderVariablesPanel = function(instance) {
        var html = '';
        html += '<div class="zato-debugger-panel zato-debugger-variables empty" data-panel-id="variables" draggable="true">';
        html += '<div class="zato-debugger-panel-header" data-panel="variables">';
        html += '<span class="zato-debugger-panel-toggle">' + UI.getChevronIcon() + '</span>';
        html += '<span class="zato-debugger-panel-title">Variables</span>';
        html += '<button class="zato-debugger-copy-btn" data-copy="variables" data-tooltip="Copy to clipboard">Copy</button>';
        html += '</div>';
        html += '<div class="zato-debugger-panel-content">';
        html += '<div class="zato-debugger-variables-list"><div class="zato-debugger-empty">No variables</div></div>';
        html += '</div>';
        html += '</div>';
        return html;
    };

    UI.renderWatchesPanel = function(instance) {
        var html = '';
        html += '<div class="zato-debugger-panel zato-debugger-watches empty" data-panel-id="watches" draggable="true">';
        html += '<div class="zato-debugger-panel-header" data-panel="watches">';
        html += '<span class="zato-debugger-panel-toggle">' + UI.getChevronIcon() + '</span>';
        html += '<span class="zato-debugger-panel-title">Watch</span>';
        html += '<button class="zato-debugger-panel-action" data-action="add-watch" title="Add expression">';
        html += UI.getPlusIcon();
        html += '</button>';
        html += '</div>';
        html += '<div class="zato-debugger-panel-content">';
        html += '<div class="zato-debugger-watches-list"><div class="zato-debugger-empty">No watch expressions</div></div>';
        html += '<div class="zato-debugger-watch-input-wrapper">';
        html += '<span class="zato-debugger-console-prompt">&gt;</span>';
        html += '<input type="text" class="zato-debugger-watch-input" placeholder="Add expression ..">';
        html += '</div>';
        html += '</div>';
        html += '</div>';
        return html;
    };

    UI.renderBreakpointsPanel = function(instance) {
        var html = '';
        html += '<div class="zato-debugger-panel zato-debugger-breakpoints empty" data-panel-id="breakpoints" draggable="true">';
        html += '<div class="zato-debugger-panel-header" data-panel="breakpoints">';
        html += '<span class="zato-debugger-panel-toggle">' + UI.getChevronIcon() + '</span>';
        html += '<span class="zato-debugger-panel-title">Breakpoints</span>';
        html += '<button class="zato-debugger-panel-action" data-action="clear-breakpoints" data-tooltip="Remove all breakpoints">';
        html += UI.getTrashIcon();
        html += '</button>';
        html += '</div>';
        html += '<div class="zato-debugger-panel-content">';
        html += '<div class="zato-debugger-breakpoints-list"><div class="zato-debugger-empty">No breakpoints</div></div>';
        html += '</div>';
        html += '</div>';
        return html;
    };

    UI.renderConsolePanel = function(instance) {
        var html = '';
        html += '<div class="zato-debugger-panel zato-debugger-console" data-panel-id="console" draggable="true">';
        html += '<div class="zato-debugger-panel-header" data-panel="console">';
        html += '<span class="zato-debugger-panel-toggle">' + UI.getChevronIcon() + '</span>';
        html += '<span class="zato-debugger-panel-title">Debug console</span>';
        html += '<button class="zato-debugger-panel-action" data-action="clear-console" data-tooltip="Clear console">';
        html += UI.getTrashIcon();
        html += '</button>';
        html += '</div>';
        html += '<div class="zato-debugger-panel-content zato-debugger-console-content">';
        html += '<div class="zato-debugger-console-output"></div>';
        html += '<div class="zato-debugger-console-input-wrapper">';
        html += '<span class="zato-debugger-console-prompt">&gt;</span>';
        html += '<input type="text" class="zato-debugger-console-input" placeholder="Evaluate expression ..">';
        html += '</div>';
        html += '</div>';
        html += '</div>';
        return html;
    };

})();
