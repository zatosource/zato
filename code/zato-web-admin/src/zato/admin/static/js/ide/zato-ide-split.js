(function() {
    'use strict';

    /**
     * ZatoIDESplit - resizable split container with two panels.
     *
     * This component creates a horizontally split container with a draggable
     * resizer between two panels (left and right).
     *
     * Usage:
     *   var instance = ZatoIDESplit.create('my-container-id', {
     *       onResize: function(instance) { console.log('resized'); }
     *   });
     *
     *   var leftPanel = ZatoIDESplit.getLeftPanel(instance);
     *   var rightPanel = ZatoIDESplit.getRightPanel(instance);
     *
     *   ZatoIDESplit.destroy('my-container-id');
     *
     * The container element must exist in the DOM before calling create().
     * Split position is automatically persisted to localStorage.
     *
     * localStorage key: 'zato.ide.split-position' (stores percentage as float)
     *
     * CSS classes used:
     *   - .zato-ide-split-container - flex container for the split
     *   - .zato-ide-split-panel - base class for panels
     *   - .zato-ide-split-panel-left - left panel
     *   - .zato-ide-split-panel-right - right panel
     *   - .zato-ide-split-resizer - draggable divider between panels
     */
    var ZatoIDESplit = {

        /**
         * localStorage key for persisting split position.
         */
        storageKey: 'zato.ide.split-position',

        /**
         * Default split position as percentage (0-100).
         * 50 means equal width for both panels.
         */
        defaultSplitPercent: 50,

        /**
         * Fallback width in pixels from the right edge when exact position cannot be restored.
         */
        fallbackRightPanelWidth: 300,

        /**
         * Minimum width in pixels for either panel.
         * Prevents panels from being resized too small.
         */
        minPanelWidth: 200,

        /**
         * Map of container ID to instance object.
         */
        instances: {},

        /**
         * Creates a new split container instance.
         *
         * @param {string} containerId - ID of the DOM element to render into
         * @param {Object} options - configuration options
         * @param {Function} options.onResize - callback fired after resize ends
         * @returns {Object|null} instance object, or null if container not found
         *
         * The returned instance object contains:
         *   - id: the container ID
         *   - container: the DOM element
         *   - splitPercent: current split position (0-100)
         *   - isDragging: whether resizer is being dragged
         *   - leftPanel: left panel DOM element
         *   - rightPanel: right panel DOM element
         *   - resizer: resizer DOM element
         *   - onResize: callback function
         */
        create: function(containerId, options) {
            var opts = options || {};
            var container = document.getElementById(containerId);
            if (!container) {
                console.error('ZatoIDESplit: container not found:', containerId);
                return null;
            }

            var storageKey = opts.storageKey || this.storageKey;
            var defaultPercent = opts.defaultSplitPercent || this.defaultSplitPercent;
            var fallbackRightPanelWidth = opts.fallbackRightPanelWidth || this.fallbackRightPanelWidth;

            var instance = {
                id: containerId,
                container: container,
                splitPercent: defaultPercent,
                savedLeftPanelPixels: null,
                isDragging: false,
                leftPanel: null,
                rightPanel: null,
                resizer: null,
                onResize: opts.onResize || null,
                storageKey: storageKey,
                defaultSplitPercent: defaultPercent,
                fallbackRightPanelWidth: fallbackRightPanelWidth,
                minPanelWidth: opts.minPanelWidth || this.minPanelWidth
            };

            this.render(instance);
            this.bindEvents(instance);
            this.restoreSplitPosition(instance);
            this.instances[containerId] = instance;

            return instance;
        },

        /**
         * Renders the split container HTML structure.
         * Called automatically by create(). Structure:
         *   - .zato-ide-split-container
         *     - .zato-ide-split-panel.zato-ide-split-panel-left
         *     - .zato-ide-split-resizer (draggable)
         *     - .zato-ide-split-panel.zato-ide-split-panel-right
         *
         * @param {Object} instance - the split instance object
         */
        render: function(instance) {
            var html = '';

            html += '<div class="zato-ide-split-container">';

            html += '<div class="zato-ide-split-panel zato-ide-split-panel-left" id="' + instance.id + '-left-panel">';
            html += '</div>';

            html += '<div class="zato-ide-split-resizer" id="' + instance.id + '-resizer"></div>';

            html += '<div class="zato-ide-split-panel zato-ide-split-panel-right" id="' + instance.id + '-right-panel">';
            html += '</div>';

            html += '</div>';

            instance.container.innerHTML = html;

            instance.leftPanel = document.getElementById(instance.id + '-left-panel');
            instance.rightPanel = document.getElementById(instance.id + '-right-panel');
            instance.resizer = document.getElementById(instance.id + '-resizer');

            this.applySplitPosition(instance);
        },

        /**
         * Binds mouse event listeners for resizer dragging.
         * Handles mousedown on resizer, mousemove on document, mouseup on document.
         * Saves split position to localStorage when drag ends.
         *
         * @param {Object} instance - the split instance object
         */
        bindEvents: function(instance) {
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
                var snapThreshold = 50;

                var iconsEl = instance.rightPanel ? instance.rightPanel.querySelector('.zato-ide-side-panel-1-icons') : null;
                var iconsWidth = iconsEl ? iconsEl.offsetWidth : 48;
                var collapsedLeftWidth = containerWidth - iconsWidth - resizerWidth;

                var newIdeWidth = e.clientX - containerRect.left;
                var maxIdeWidth = containerWidth - minWidth - resizerWidth;

                console.log('[Split] mousemove: clientX=' + e.clientX + ', isDragging=' + instance.isDragging + ', wasCollapsed=' + instance.wasCollapsedOnMousedown + ', dragStartX=' + instance.dragStartX);

                if (instance.wasCollapsedOnMousedown) {
                    var dragDelta = instance.dragStartX - e.clientX;
                    console.log('[Split] expand mode: dragDelta=' + dragDelta + ', threshold=' + snapThreshold + ', willExpand=' + (dragDelta >= snapThreshold));
                    if (dragDelta >= snapThreshold) {
                        console.log('[Split] expanding now');
                        var contentEl = instance.rightPanel ? instance.rightPanel.querySelector('.zato-ide-side-panel-1-content') : null;
                        if (contentEl) {
                            contentEl.classList.remove('collapsed');
                            console.log('[Split] removed collapsed class');
                        }
                        instance.wasCollapsedOnMousedown = false;
                        instance.expandedDuringThisDrag = true;
                        instance.leftPanel.style.width = Math.round(maxIdeWidth) + 'px';
                        instance.splitPercent = (maxIdeWidth / containerWidth) * 100;
                        console.log('[Split] set leftPanel width to maxIdeWidth=' + maxIdeWidth);
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
        },

        /**
         * Applies the current split position to the left panel width.
         * Respects minPanelWidth constraints for both panels.
         *
         * @param {Object} instance - the split instance object
         */
        applySplitPosition: function(instance) {
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
        },

        /**
         * Saves the split position to localStorage as pixels.
         *
         * @param {Object} instance - the split instance object
         */
        saveSplitPosition: function(instance) {
            var key = instance.storageKey || this.storageKey;
            var leftWidth = instance.leftPanel ? instance.leftPanel.offsetWidth : 0;
            try {
                localStorage.setItem(key, leftWidth.toString());
            } catch (e) {
                console.warn('ZatoIDESplit: failed to save split position:', e);
            }
        },

        /**
         * Restores the split position from localStorage.
         * Applies fallback logic if exact position cannot be restored.
         *
         * @param {Object} instance - the split instance object
         */
        restoreSplitPosition: function(instance) {
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
            var resizerWidth = instance.resizer ? instance.resizer.offsetWidth : 4;
            var minWidth = instance.minPanelWidth;
            var fallbackRightWidth = instance.fallbackRightPanelWidth || this.fallbackRightPanelWidth;

            var maxLeftWidth = containerWidth - minWidth - resizerWidth;

            if (savedPixels >= minWidth && savedPixels <= maxLeftWidth) {
                instance.leftPanel.style.width = savedPixels + 'px';
                instance.splitPercent = (savedPixels / containerWidth) * 100;
                return;
            }

            var fallbackLeftWidth = containerWidth - fallbackRightWidth - resizerWidth;
            if (fallbackLeftWidth >= minWidth && fallbackLeftWidth <= maxLeftWidth) {
                instance.leftPanel.style.width = Math.round(fallbackLeftWidth) + 'px';
                instance.splitPercent = (fallbackLeftWidth / containerWidth) * 100;
                return;
            }

            var contentEl = instance.rightPanel ? instance.rightPanel.querySelector('.zato-ide-side-panel-1-content') : null;
            if (contentEl) {
                contentEl.classList.add('collapsed');
            }
            var iconsEl = instance.rightPanel ? instance.rightPanel.querySelector('.zato-ide-side-panel-1-icons') : null;
            var iconsWidth = iconsEl ? iconsEl.offsetWidth : 48;
            var collapsedLeftWidth = containerWidth - iconsWidth - resizerWidth;
            if (collapsedLeftWidth >= minWidth) {
                instance.leftPanel.style.width = Math.round(collapsedLeftWidth) + 'px';
            }
        },

        /**
         * Collapses the right panel, expanding the left panel to fill the space.
         * Stores the previous split position for restoration.
         *
         * @param {Object} instance - the split instance object
         */
        collapseRightPanel: function(instance) {
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
        },

        /**
         * Expands the right panel, restoring the previous split position.
         *
         * @param {Object} instance - the split instance object
         */
        expandRightPanel: function(instance) {
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
        },

        /**
         * Toggles the right panel collapsed state.
         *
         * @param {Object} instance - the split instance object
         */
        toggleRightPanel: function(instance) {
            if (!instance) {
                return;
            }
            if (instance.rightPanelCollapsed) {
                this.expandRightPanel(instance);
            } else {
                this.collapseRightPanel(instance);
            }
        },

        /**
         * Returns the left panel element.
         *
         * @param {Object} instance - the split instance object
         * @returns {HTMLElement|null} the left panel element
         */
        getLeftPanel: function(instance) {
            return instance ? instance.leftPanel : null;
        },

        /**
         * Alias for getLeftPanel (backward compatibility).
         */
        getIDEPanel: function(instance) {
            return this.getLeftPanel(instance);
        },

        /**
         * Returns the right panel element.
         *
         * @param {Object} instance - the split instance object
         * @returns {HTMLElement|null} the right panel element
         */
        getRightPanel: function(instance) {
            return instance ? instance.rightPanel : null;
        },

        /**
         * Alias for getRightPanel (backward compatibility).
         */
        getChatPanel: function(instance) {
            return this.getRightPanel(instance);
        },

        /**
         * Retrieves an existing split instance by container ID.
         *
         * @param {string} containerId - ID of the container element
         * @returns {Object|null} the instance object, or null if not found
         */
        getInstance: function(containerId) {
            return this.instances[containerId] || null;
        },

        /**
         * Destroys a split instance and clears its container.
         * Removes the instance from the internal registry.
         *
         * @param {string} containerId - ID of the container element
         */
        destroy: function(containerId) {
            var instance = this.instances[containerId];
            if (instance) {
                instance.container.innerHTML = '';
                delete this.instances[containerId];
            }
        }
    };

    window.ZatoIDESplit = ZatoIDESplit;

})();
