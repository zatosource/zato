'use strict';

// The Settings control in the top right corner of every screen. For now
// it holds one section, Theme: clicking a theme applies it instantly by
// setting data-theme on the html element - no restart, no page reload -
// and the choice persists in localStorage. The list of installed themes
// comes from themes-index.js, which the theme converter generates.

(function() {

var settingsView = {

    config: {
        storageKey: 'ui-theme',
        defaultTheme: 'zato-default',
    },

    // The button is remembered so the panel can re-render in place when
    // a theme is applied, moving the active marker without closing
    anchorButton: null,

// ////////////////////////////////////////////////////////////////////////

    currentTheme: function() {
        var stored = window.localStorage.getItem(this.config.storageKey);
        if (stored === null) { stored = this.config.defaultTheme; }
        return stored;
    },

// ////////////////////////////////////////////////////////////////////////

    openPanel: function(button) {
        if (shared.panelElement !== null) { shared.closePanel(); return; }
        this.anchorButton = button;
        this.renderPanel();
    },

    renderPanel: function() {
        var current = this.currentTheme();
        var html = '<div class="settings-panel-title">Settings</div>' +
            '<div class="settings-section-title">Theme</div>';

        window.themesIndex.forEach(function(theme) {
            var active = theme.slug === current;
            html += '<button class="settings-theme-entry' + (active ? ' settings-theme-active' : '') + '" ' +
                'onclick="settingsView.applyTheme(\'' + theme.slug + '\')">' +
                '<span>' + theme.name + '</span>' +
                '<span class="settings-theme-kind">' + theme.type + (active ? ' \u00b7 active' : '') + '</span>' +
                '</button>';
        });

        html += '<div class="floating-panel-hint">Applies right away, nothing reloads. The choice sticks in this browser.</div>';
        shared.openPanel(this.anchorButton, html);
    },

// ////////////////////////////////////////////////////////////////////////

    applyTheme: function(slug) {
        document.documentElement.dataset.theme = slug;
        window.localStorage.setItem(this.config.storageKey, slug);

        // The panel stays open with the active marker moved, so trying
        // themes one after another costs one click each
        this.renderPanel();
    },
};

window.settingsView = settingsView;

// The button lives at the right end of the topbar line on every screen
var topbarLine = document.querySelector('.main-topbar-line');
var settingsButton = document.createElement('button');
settingsButton.className = 'settings-button';
settingsButton.id = 'settings-button';
settingsButton.textContent = 'Settings';
settingsButton.addEventListener('click', function() { settingsView.openPanel(settingsButton); });
topbarLine.appendChild(settingsButton);

})();
