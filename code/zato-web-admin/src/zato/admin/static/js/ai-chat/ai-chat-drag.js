(function() {
    'use strict';

    var AIChatDrag = {
        isDragging: false,
        isResizing: false,
        resizeState: null,
        dragOffsetX: 0,
        dragOffsetY: 0,

        isTabDragging: false,
        draggedTabId: null,
        draggedTabElement: null,
        dragClone: null,
        tabDragOffsetX: 0,
        tabDragOffsetY: 0,
        tabOriginalWidth: 0,
        tabOriginalIndex: 0,
        pendingDropIndex: null,
        tabDragStartX: 0,
        tabDragStartY: 0,
        tabDragThreshold: 5,
        tabDragActivated: false,

        handleMouseDown: function(e, widget, isMinimized, zoomScale, toggleMinimizeCallback) {
            var target = e.target;

            if (target.id === 'ai-chat-header' || target.closest('#ai-chat-header')) {
                if (target.classList.contains('ai-chat-header-button')) {
                    return false;
                }

                if (isMinimized) {
                    toggleMinimizeCallback();
                    e.preventDefault();
                    return true;
                }

                this.isDragging = true;
                AIChatResize.convertToLeftTop(widget);

                var rect = widget.getBoundingClientRect();
                this.dragOffsetX = e.clientX - rect.left;
                this.dragOffsetY = e.clientY - rect.top;

                e.preventDefault();
                return true;
            }

            if (target.classList.contains('ai-chat-resize-handle')) {
                AIChatResize.convertToLeftTop(widget);
                this.resizeState = AIChatResize.startResize(widget, e, target.getAttribute('data-direction'));
                this.isResizing = true;
                e.preventDefault();
                return true;
            }

            var tabElement = target.closest('.ai-chat-tab');
            if (tabElement && !target.classList.contains('ai-chat-tab-close')) {
                if (tabElement.classList.contains('pinned') || tabElement.classList.contains('locked')) {
                    return false;
                }
                this.isTabDragging = true;
                this.tabDragActivated = false;
                this.draggedTabId = tabElement.getAttribute('data-tab-id');
                this.draggedTabElement = tabElement;
                this.tabDragStartX = e.clientX;
                this.tabDragStartY = e.clientY;

                var tabRect = tabElement.getBoundingClientRect();
                this.tabDragOffsetX = e.clientX - tabRect.left;
                this.tabDragOffsetY = e.clientY - tabRect.top;
                this.tabOriginalWidth = tabRect.width;
                this.tabOriginalIndex = Array.from(tabElement.parentNode.children).indexOf(tabElement);

                e.preventDefault();
                return true;
            }

            return false;
        },

        handleMouseMove: function(e, widget, zoomScale) {
            if (this.isDragging) {
                AIChatResize.handleDrag(widget, e, this.dragOffsetX, this.dragOffsetY, zoomScale);
                return;
            }

            if (this.isResizing && this.resizeState) {
                AIChatResize.handleResize(widget, e, this.resizeState);
                return;
            }

            if (this.isTabDragging) {
                if (!this.tabDragActivated) {
                    var dx = e.clientX - this.tabDragStartX;
                    var dy = e.clientY - this.tabDragStartY;
                    var distance = Math.sqrt(dx * dx + dy * dy);
                    if (distance < this.tabDragThreshold) {
                        return;
                    }
                    this.tabDragActivated = true;
                    var tabRect = this.draggedTabElement.getBoundingClientRect();
                    var clone = this.draggedTabElement.cloneNode(true);
                    clone.classList.add('dragging');
                    clone.style.width = tabRect.width + 'px';
                    clone.style.left = tabRect.left + 'px';
                    clone.style.top = tabRect.top + 'px';
                    clone.id = 'ai-chat-tab-drag-clone';
                    document.body.appendChild(clone);
                    this.dragClone = clone;
                    this.draggedTabElement.style.opacity = '0.3';
                }

                if (!this.dragClone) {
                    return;
                }

                var newLeft = e.clientX - this.tabDragOffsetX;
                var newTop = e.clientY - this.tabDragOffsetY;
                this.dragClone.style.left = newLeft + 'px';
                this.dragClone.style.top = newTop + 'px';

                this.pendingDropIndex = null;
                var tabsContainer = widget.querySelector('#ai-chat-tabs');
                var tabs = tabsContainer.querySelectorAll('.ai-chat-tab');

                for (var i = 0; i < tabs.length; i++) {
                    var tab = tabs[i];
                    if (tab === this.draggedTabElement) continue;
                    var rect = tab.getBoundingClientRect();
                    var midX = rect.left + rect.width / 2;

                    if (e.clientX > rect.left && e.clientX < rect.right) {
                        if (e.clientX < midX) {
                            this.pendingDropIndex = Array.from(tabsContainer.children).indexOf(tab);
                        } else {
                            this.pendingDropIndex = Array.from(tabsContainer.children).indexOf(tab) + 1;
                        }
                        break;
                    }
                }
            }
        },

        handleMouseUp: function(widget, tabs, saveCallback, renderCallback) {
            var result = { tabsChanged: false, tabs: tabs };

            if (this.isDragging) {
                this.isDragging = false;
                AIChatWidget.savePosition(widget);
            }

            if (this.isResizing) {
                this.isResizing = false;
                this.resizeState = null;
                AIChatWidget.saveDimensions(widget);
                AIChatWidget.savePosition(widget);
            }

            if (this.isTabDragging) {
                this.isTabDragging = false;

                if (this.tabDragActivated) {
                    if (this.dragClone && this.dragClone.parentNode) {
                        this.dragClone.parentNode.removeChild(this.dragClone);
                        this.dragClone = null;
                    }

                    if (this.draggedTabElement) {
                        this.draggedTabElement.style.opacity = '';
                    }

                    if (this.pendingDropIndex !== null && this.pendingDropIndex !== undefined) {
                        var draggedTabIndex = AIChatTabs.getTabIndex(tabs, this.draggedTabId);
                        if (draggedTabIndex !== -1 && draggedTabIndex !== this.pendingDropIndex) {
                            var draggedTab = tabs[draggedTabIndex];

                            var pinnedCount = 0;
                            for (var i = 0; i < tabs.length; i++) {
                                if (tabs[i].pinned) {
                                    pinnedCount++;
                                } else {
                                    break;
                                }
                            }

                            var insertAt = this.pendingDropIndex;
                            if (insertAt > draggedTabIndex) {
                                insertAt = insertAt - 1;
                            }

                            if (!draggedTab.pinned && insertAt < pinnedCount) {
                                insertAt = pinnedCount;
                            }

                            if (draggedTabIndex !== insertAt) {
                                var tab = tabs.splice(draggedTabIndex, 1)[0];
                                tabs.splice(insertAt, 0, tab);
                                result.tabsChanged = true;
                                result.tabs = tabs;
                            }
                        }
                    }
                }

                this.draggedTabId = null;
                this.draggedTabElement = null;
                this.tabDragActivated = false;
            }

            return result;
        }
    };

    window.AIChatDrag = AIChatDrag;

})();
