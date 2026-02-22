(function() {
    'use strict';

    var ZatoIDESplit = window.ZatoIDESplit;

    ZatoIDESplit.bindEvents = function(instance) {
        var self = this;

        instance.resizer.addEventListener('mousedown', function(e) {
            e.preventDefault();
            instance.isDragging = true;
            instance.hasDragged = false;
            instance.resizer.classList.add('dragging');
            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';

            var contentEl = instance.rightPanel ? instance.rightPanel.querySelector('.zato-ide-side-panel-1-content') : null;
            instance.wasCollapsedOnMousedown = contentEl && contentEl.classList.contains('collapsed');
            instance.expandedDuringThisDrag = false;
            instance.dragStartX = e.clientX;
            console.log('[Split] mousedown: wasCollapsedOnMousedown=' + instance.wasCollapsedOnMousedown + ', startX=' + e.clientX);
        });

        instance.resizer.addEventListener('click', function(e) {
            if (instance.hasDragged) {
                instance.wasCollapsedOnMousedown = false;
                return;
            }
            if (instance.wasCollapsedOnMousedown) {
                var contentEl = instance.rightPanel ? instance.rightPanel.querySelector('.zato-ide-side-panel-1-content') : null;
                if (contentEl) {
                    contentEl.classList.add('collapsed');
                }
                if (typeof ZatoIDEKeyboard !== 'undefined' && ZatoIDEKeyboard.toggleSidePanelContent) {
                    ZatoIDEKeyboard.toggleSidePanelContent();
                }
            } else {
                if (typeof ZatoIDEKeyboard !== 'undefined' && ZatoIDEKeyboard.toggleSidePanelContent) {
                    ZatoIDEKeyboard.toggleSidePanelContent();
                }
            }
            instance.wasCollapsedOnMousedown = false;
        });

        document.addEventListener('mousemove', function(e) {
            if (!instance.isDragging) {
                return;
            }

            instance.hasDragged = true;

            var containerRect = instance.container.getBoundingClientRect();
            var containerWidth = containerRect.width;
            var resizerWidth = instance.resizer.offsetWidth;
            var minWidth = instance.minPanelWidth;
            var snapThreshold = self.snapThreshold;

            var iconsEl = instance.rightPanel ? instance.rightPanel.querySelector('.zato-ide-side-panel-1-icons') : null;
            var iconsWidth = iconsEl ? iconsEl.offsetWidth : 48;
            var collapsedLeftWidth = containerWidth - iconsWidth - resizerWidth;

            var newIdeWidth = e.clientX - containerRect.left;
            var maxIdeWidth = containerWidth - minWidth - resizerWidth;

            console.log('[Split] mousemove: clientX=' + e.clientX + ', isDragging=' + instance.isDragging + ', wasCollapsed=' + instance.wasCollapsedOnMousedown + ', dragStartX=' + instance.dragStartX);

            if (instance.wasCollapsedOnMousedown) {
                var dragDelta = instance.dragStartX - e.clientX;
                console.log('[Split] expand mode: dragDelta=' + dragDelta + ', threshold=' + snapThreshold + ', willExpand=' + (dragDelta >= snapThreshold));
                var expandStartThreshold = Math.round(snapThreshold * self.expandStartPercent / 100);
                if (dragDelta >= expandStartThreshold) {
                    var contentEl = instance.rightPanel ? instance.rightPanel.querySelector('.zato-ide-side-panel-1-content') : null;
                    if (contentEl) {
                        contentEl.classList.remove('collapsed');
                    }
                    instance.wasCollapsedOnMousedown = false;
                    instance.expandedDuringThisDrag = true;
                    instance.leftPanel.style.width = Math.round(maxIdeWidth) + 'px';
                    instance.splitPercent = (maxIdeWidth / containerWidth) * 100;
                    return;
                } else {
                    return;
                }
            }

            if (instance.expandedDuringThisDrag && newIdeWidth <= maxIdeWidth) {
                instance.expandedDuringThisDrag = false;
                instance.dragStartX = e.clientX;
            }

            if (newIdeWidth > maxIdeWidth && !instance.expandedDuringThisDrag) {
                var overDrag = newIdeWidth - maxIdeWidth;
                if (overDrag >= snapThreshold) {
                    var contentEl = instance.rightPanel ? instance.rightPanel.querySelector('.zato-ide-side-panel-1-content') : null;
                    if (contentEl) {
                        contentEl.classList.add('collapsed');
                    }
                    instance.leftPanel.style.width = Math.round(collapsedLeftWidth) + 'px';
                    instance.splitPercent = (collapsedLeftWidth / containerWidth) * 100;
                    instance.wasCollapsedOnMousedown = true;
                    instance.expandedDuringThisDrag = false;
                    instance.dragStartX = e.clientX;
                    self.saveSplitPosition(instance);
                    if (instance.onResize) {
                        instance.onResize(instance);
                    }
                    return;
                }
                newIdeWidth = maxIdeWidth;
            }

            if (newIdeWidth < minWidth) {
                newIdeWidth = minWidth;
            }

            instance.splitPercent = (newIdeWidth / containerWidth) * 100;
            self.applySplitPosition(instance);

        });

        document.addEventListener('mouseup', function() {
            if (instance.isDragging) {
                console.log('[Split] mouseup: saving position');
                instance.isDragging = false;
                instance.resizer.classList.remove('dragging');
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
                self.saveSplitPosition(instance);

                if (instance.onResize) {
                    instance.onResize(instance);
                }
            }
        });
    };

})();
