'use strict';

(function() {

var settingsView = {

    config: {
        storageKey: 'ui-theme',
        defaultTheme: window.themesDefault,
    },

    anchorButton: null,

// ////////////////////////////////////////////////////////////////////////

    currentTheme: function() {
        var stored = window.localStorage.getItem(this.config.storageKey);

        var shipped = window.themesIndex.some(function(theme) { return theme.slug === stored; });
        if (!shipped) { stored = this.config.defaultTheme; }

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
            var marker = active ? '<span class="settings-theme-kind">active</span>' : '';

            html += '<button class="settings-theme-entry' + (active ? ' settings-theme-active' : '') + '" ' +
                'onclick="settingsView.applyTheme(\'' + theme.slug + '\')">' +
                '<span>' + theme.name + '</span>' + marker +
                '</button>';
        });

        shared.openPanel(this.anchorButton, html);
    },

// ////////////////////////////////////////////////////////////////////////

    applyTheme: function(slug) {
        document.documentElement.dataset.theme = slug;
        window.localStorage.setItem(this.config.storageKey, slug);
        this.renderPanel();
    },
};

window.settingsView = settingsView;

var settingsButton = document.createElement('button');
settingsButton.className = 'settings-button';
settingsButton.id = 'settings-button';
settingsButton.textContent = 'Settings';
settingsButton.addEventListener('click', function() { settingsView.openPanel(settingsButton); });

// Screens with a bar of their own keep the button at its right end, the plain ones open with it
var bar = document.querySelector('.command-bar, .toolbar');

if (bar === null) {
    var content = document.querySelector('.main-content');
    content.insertBefore(settingsButton, content.firstChild);
} else {
    bar.appendChild(settingsButton);
}

})();
