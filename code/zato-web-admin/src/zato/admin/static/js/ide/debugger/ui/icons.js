(function() {
    'use strict';

    var UI = window.ZatoDebuggerUI;

    UI.getContinueIcon = function() {
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><path d="M3 2l10 6-10 6V2z"/></svg>';
    };

    UI.getPauseIcon = function() {
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><rect x="3" y="2" width="4" height="12"/><rect x="9" y="2" width="4" height="12"/></svg>';
    };

    UI.getStepOverIcon = function() {
        return '/static/img/debugger/step-over.svg';
    };

    UI.getStepIntoIcon = function() {
        return '/static/img/debugger/step-into.svg';
    };

    UI.getStepOutIcon = function() {
        return '/static/img/debugger/step-out.svg';
    };

    UI.getRestartIcon = function() {
        return '/static/img/debugger/restart.svg';
    };

    UI.getStopIcon = function() {
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><rect x="3" y="3" width="10" height="10"/></svg>';
    };

    UI.getChevronIcon = function() {
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="12" height="12" fill="currentColor"><path d="M6 4l4 4-4 4"/></svg>';
    };

    UI.getPlusIcon = function() {
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="14" height="14" fill="currentColor"><path d="M8 2v12M2 8h12"/></svg>';
    };

    UI.getTrashIcon = function() {
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="14" height="14" fill="currentColor"><path d="M5 2V1h6v1h4v2H1V2h4zm1 3h1v8H6V5zm3 0h1v8H9V5zM3 4v10h10V4H3z"/></svg>';
    };

    UI.getCloseIcon = function() {
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="12" height="12" fill="currentColor"><path d="M12 4L4 12M4 4l8 8"/></svg>';
    };

    UI.getBreakpointIcon = function() {
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="12" height="12" fill="#e51400"><circle cx="8" cy="8" r="6"/></svg>';
    };

})();
