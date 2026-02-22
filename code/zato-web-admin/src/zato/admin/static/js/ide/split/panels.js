(function() {
    'use strict';

    var ZatoIDESplit = window.ZatoIDESplit;

    ZatoIDESplit.collapseRightPanel = function(instance) {
        if (!instance || instance.rightPanelCollapsed) {
            return;
        }
        instance.savedSplitPercent = instance.splitPercent;
        instance.rightPanelCollapsed = true;
        if (instance.rightPanel) {
            instance.rightPanel.style.display = 'none';
        }
        if (instance.resizer) {
            instance.resizer.style.display = 'none';
        }
        if (instance.leftPanel) {
            instance.leftPanel.style.width = '100%';
        }
        if (instance.onResize) {
            instance.onResize(instance);
        }
    };

    ZatoIDESplit.expandRightPanel = function(instance) {
        if (!instance || !instance.rightPanelCollapsed) {
            return;
        }
        instance.rightPanelCollapsed = false;
        if (instance.rightPanel) {
            instance.rightPanel.style.display = '';
        }
        if (instance.resizer) {
            instance.resizer.style.display = '';
        }
        if (instance.savedSplitPercent !== undefined) {
            instance.splitPercent = instance.savedSplitPercent;
        }
        this.applySplitPosition(instance);
        if (instance.onResize) {
            instance.onResize(instance);
        }
    };

    ZatoIDESplit.toggleRightPanel = function(instance) {
        if (!instance) {
            return;
        }
        if (instance.rightPanelCollapsed) {
            this.expandRightPanel(instance);
        } else {
            this.collapseRightPanel(instance);
        }
    };

    ZatoIDESplit.getLeftPanel = function(instance) {
        return instance ? instance.leftPanel : null;
    };

    ZatoIDESplit.getIDEPanel = function(instance) {
        return this.getLeftPanel(instance);
    };

    ZatoIDESplit.getRightPanel = function(instance) {
        return instance ? instance.rightPanel : null;
    };

    ZatoIDESplit.getChatPanel = function(instance) {
        return this.getRightPanel(instance);
    };

})();
