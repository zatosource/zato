(function() {
    'use strict';

    var ZatoIDESplit = window.ZatoIDESplit;

    ZatoIDESplit.applySplitPosition = function(instance) {
        var containerWidth = instance.container.offsetWidth;
        var resizerWidth = instance.resizer ? instance.resizer.offsetWidth : 4;
        var minWidth = instance.minPanelWidth;
        var leftWidth = (containerWidth * instance.splitPercent / 100);

        if (leftWidth < minWidth) {
            leftWidth = minWidth;
        }

        var maxLeftWidth = containerWidth - minWidth - resizerWidth;
        if (leftWidth > maxLeftWidth) {
            leftWidth = maxLeftWidth;
        }

        if (instance.leftPanel) {
            instance.leftPanel.style.width = Math.round(leftWidth) + 'px';
        }
    };

    ZatoIDESplit.saveSplitPosition = function(instance) {
        var key = instance.storageKey || this.storageKey;
        var leftWidth = instance.leftPanel ? instance.leftPanel.offsetWidth : 0;
        try {
            localStorage.setItem(key, leftWidth.toString());
        } catch (e) {
            console.warn('ZatoIDESplit: failed to save split position:', e);
        }
    };

    ZatoIDESplit.restoreSplitPosition = function(instance) {
        var key = instance.storageKey || this.storageKey;
        var savedPixels = null;
        try {
            var saved = localStorage.getItem(key);
            if (saved !== null) {
                savedPixels = parseInt(saved, 10);
                if (isNaN(savedPixels) || savedPixels < 0) {
                    savedPixels = null;
                }
            }
        } catch (e) {
            console.warn('ZatoIDESplit: failed to load split position:', e);
        }

        if (savedPixels === null) {
            return;
        }

        var containerWidth = instance.container.offsetWidth;
        instance.leftPanel.style.width = savedPixels + 'px';
        instance.splitPercent = (savedPixels / containerWidth) * 100;
    };

})();
