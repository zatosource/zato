// selection.js - Element selection functionality with rubber-band selection

class Selection {
    constructor(graph, paper) {
        this.graph = graph;
        this.paper = paper;
        this.selectedElements = [];
        this.isPanning = false;
        this.eventProxies = [];

        // Rubber-band selection state
        this.selectionBox = null;
        this.selectionStartPosition = null;
        this.isSelecting = false;

        // Add CSS styles for selection highlighting
        const color = "#2196F3";
        const styleElement = document.createElement('style');
        styleElement.textContent = `
            .joint-element .selection-highlight {
                stroke: ${color};
                stroke-width: 3px;
                stroke-dasharray: 5,5;
            }
            .joint-link .selection-highlight {
                stroke: ${color};
                stroke-dasharray: 5,5;
                stroke-dashoffset: 10;
                animation: dash 0.5s infinite linear;
            }
            @keyframes dash {
                to {
                    stroke-dashoffset: 0;
                }
            }
            .selection-box {
                position: absolute;
                border: 2px dashed ${color};
                background-color: rgba(33, 150, 243, 0.1);
                pointer-events: none;
                z-index: 1000;
            }
        `;
        document.head.appendChild(styleElement);
        this.styleElement = styleElement; // Store reference for cleanup

        this.setupEventListeners();
        console.log("Selection manager initialized with rubber-band selection");
    }

    /**
     * Set up the event listeners for selection functionality
     */
    setupEventListeners() {
        // Group movement tracking variables
        this.dragStartPositions = {};
        this.isDragging = false;
        this.draggedElement = null;

        // Selection on element click
        const handleElementClick = (elementView, evt) => {
            console.log("Element clicked:", elementView.model.id);
            const multiSelect = evt.ctrlKey || evt.shiftKey;
            this.selectElement(elementView.model, multiSelect);
            evt.stopPropagation(); // Prevent bubble to paper blank click
        };

        // Clear selection on blank click (if not part of a rubber-band selection)
        const handleBlankClick = (evt) => {
            // If this was the end of a drag operation, don't clear the selection
            if (this.hasMovedDuringSelection) {
                console.log("Mouse moved during selection, not clearing");
                return;
            }

            console.log("Blank area clicked, clearing selection");
            this.clearSelection();
        };

        // Start rubber-band selection
        const handleBlankPointerDown = (evt, x, y) => {
            // Only start selection if not in panning mode
            if (this.isPanning) return;

            console.log("Starting rubber-band selection at", x, y);
            this.isSelecting = true;
            this.hasMovedDuringSelection = false;

            // Store actual client coordinates
            this.selectionStartPosition = {
                x: evt.clientX,
                y: evt.clientY
            };

            // Create selection box element
            this.createSelectionBox();

            // If not using modifier keys, clear the current selection
            if (!(evt.ctrlKey || evt.shiftKey)) {
                this.clearSelection();
            }
        };

        // Update rubber-band selection
        const handleMouseMove = (evt) => {
            if (!this.isSelecting) return;

            // Get current client position
            const currentPosition = {
                x: evt.clientX,
                y: evt.clientY
            };

            // Check if we've moved enough to count as a drag
            const moveThreshold = 5;
            if (!this.hasMovedDuringSelection) {
                const dx = Math.abs(currentPosition.x - this.selectionStartPosition.x);
                const dy = Math.abs(currentPosition.y - this.selectionStartPosition.y);
                if (dx > moveThreshold || dy > moveThreshold) {
                    this.hasMovedDuringSelection = true;
                }
            }

            // Update selection box
            this.updateSelectionBox(this.selectionStartPosition, currentPosition);
        };

        // Complete rubber-band selection
        const handleMouseUp = (evt) => {
            if (!this.isSelecting) return;

            console.log("Completing rubber-band selection");
            this.isSelecting = false;

            // If we actually dragged to create a selection box
            if (this.hasMovedDuringSelection) {
                // Get current client position
                const endPosition = {
                    x: evt.clientX,
                    y: evt.clientY
                };

                // Select elements within the rectangle
                this.selectElementsInRect(
                    this.selectionStartPosition,
                    endPosition,
                    evt.ctrlKey || evt.shiftKey
                );
            }

            // Clean up
            this.removeSelectionBox();
            this.selectionStartPosition = null;
        };

        // Keyboard shortcuts
        const handleKeyDown = (evt) => {
            // Ctrl+A to select all
            if ((evt.ctrlKey || evt.metaKey) && evt.key === 'a') {
                console.log("Select all shortcut");
                evt.preventDefault();
                this.selectAll();
            }

            // Delete or Backspace to remove selected elements
            if ((evt.key === 'Delete' || evt.key === 'Backspace') && this.selectedElements.length > 0) {
                console.log("Delete selection shortcut");
                evt.preventDefault();
                this.removeSelected();
            }

            // Escape to clear selection
            if (evt.key === 'Escape') {
                console.log("Clear selection shortcut");
                evt.preventDefault();
                this.clearSelection();
            }
        };

        // Group movement: Handle element drag start
        const handleElementPointerDown = (elementView, evt) => {
            if (this.isPanning) return; // Don't track dragging in panning mode

            const element = elementView.model;
            // Check if the element is in the selection
            if (this.selectedElements.some(el => el.id === element.id)) {
                console.log("Starting group drag with element:", element.id);
                this.isDragging = true;
                this.draggedElement = element;

                // Store initial positions of all selected elements
                this.dragStartPositions = {};
                this.selectedElements.forEach(el => {
                    const position = el.position();
                    if (position) {
                        this.dragStartPositions[el.id] = { ...position }; // Clone to avoid reference issues
                    }
                });
            }
        };

        // Group movement: Handle element drag move
        const handleElementPointermove = (elementView, evt, x, y) => {
            // Only handle if we're dragging a selected element
            if (!this.isDragging || !this.draggedElement) return;

            // Don't move elements in panning mode
            if (this.isPanning) return;

            // Get the dragged element's new position
            const draggedElementId = this.draggedElement.id;
            const newPosition = this.draggedElement.position();
            const startPosition = this.dragStartPositions[draggedElementId];

            if (!startPosition || !newPosition) return;

            // Calculate movement delta
            const dx = newPosition.x - startPosition.x;
            const dy = newPosition.y - startPosition.y;

            // Move all other selected elements by the same delta
            this.selectedElements.forEach(el => {
                if (el.id !== draggedElementId) {
                    const elStartPos = this.dragStartPositions[el.id];
                    // Skip if we don't have a starting position
                    if (!elStartPos) return;

                    // Move the element to its new position
                    el.position(elStartPos.x + dx, elStartPos.y + dy);
                }
            });
        };

        // Group movement: Handle element drag end
        const handleElementPointerUp = (elementView, evt) => {
            if (this.isDragging) {
                console.log("Ending group drag");
                this.isDragging = false;
                this.draggedElement = null;
                this.dragStartPositions = {};
            }
        };

        // Register event handlers
        this.paper.on('element:pointerclick', handleElementClick);
        this.paper.on('blank:pointerclick', handleBlankClick);
        this.paper.on('blank:pointerdown', handleBlankPointerDown);
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
        document.addEventListener('keydown', handleKeyDown);

        // Group movement event handlers
        this.paper.on('element:pointerdown', handleElementPointerDown);
        this.paper.on('element:pointermove', handleElementPointermove);
        this.paper.on('element:pointerup', handleElementPointerUp);

        // Store proxies for cleanup
        this.eventProxies = [
            { target: this.paper, event: 'element:pointerclick', handler: handleElementClick },
            { target: this.paper, event: 'blank:pointerclick', handler: handleBlankClick },
            { target: this.paper, event: 'blank:pointerdown', handler: handleBlankPointerDown },
            { target: document, event: 'mousemove', handler: handleMouseMove },
            { target: document, event: 'mouseup', handler: handleMouseUp },
            { target: document, event: 'keydown', handler: handleKeyDown },
            { target: this.paper, event: 'element:pointerdown', handler: handleElementPointerDown },
            { target: this.paper, event: 'element:pointermove', handler: handleElementPointermove },
            { target: this.paper, event: 'element:pointerup', handler: handleElementPointerUp }
        ];

        console.log("Event listeners set up");
    }

    /**
     * Create a selection box for rubber-band selection
     */
    createSelectionBox() {
        // Remove any existing selection box
        this.removeSelectionBox();

        // Create a new selection box
        this.selectionBox = document.createElement('div');
        this.selectionBox.className = 'selection-box';

        // Critical: Ensure the box uses absolute positioning
        this.selectionBox.style.position = 'absolute';

        // Get the paper element and its parent
        const paperEl = this.paper.el;

        // Find the nearest positioned ancestor (for absolute positioning reference)
        // This is critical - the box must be positioned relative to the same
        // container that provides positioning context for the paper element
        let container = paperEl.parentNode;

        // Check if we can find the main-content div which is the ideal container
        const mainContent = document.querySelector('.main-content');
        if (mainContent && paperEl.closest('.main-content') === mainContent) {
            container = mainContent;
        }

        // Append to the container
        if (container) {
            container.appendChild(this.selectionBox);
        } else {
            // Fallback to paper's parent
            if (paperEl.parentNode) {
                paperEl.parentNode.appendChild(this.selectionBox);
            }
        }

        // Initially hidden
        this.selectionBox.style.display = 'none';
    }

    /**
     * Update the selection box dimensions
     * @param {Object} startPos - Starting position in client coordinates {x, y}
     * @param {Object} endPos - Current position in client coordinates {x, y}
     */
    updateSelectionBox(startPos, endPos) {
        if (!this.selectionBox) return;

        // Get the paper element position
        const paperRect = this.paper.el.getBoundingClientRect();

        // Get the container element position (the selection box's parent)
        const containerRect = this.selectionBox.parentNode.getBoundingClientRect();

        // Convert client coordinates to container-relative coordinates
        const containerStartX = startPos.x - containerRect.left;
        const containerStartY = startPos.y - containerRect.top;
        const containerEndX = endPos.x - containerRect.left;
        const containerEndY = endPos.y - containerRect.top;

        // Calculate dimensions
        const left = Math.min(containerStartX, containerEndX);
        const top = Math.min(containerStartY, containerEndY);
        const width = Math.abs(containerEndX - containerStartX);
        const height = Math.abs(containerEndY - containerStartY);

        // Update styles with container-relative coordinates
        this.selectionBox.style.left = `${left}px`;
        this.selectionBox.style.top = `${top}px`;
        this.selectionBox.style.width = `${width}px`;
        this.selectionBox.style.height = `${height}px`;
        this.selectionBox.style.display = 'block';
    }

    /**
     * Remove the selection box
     */
    removeSelectionBox() {
        if (this.selectionBox && this.selectionBox.parentNode) {
            this.selectionBox.parentNode.removeChild(this.selectionBox);
            this.selectionBox = null;
        }
    }

    /**
     * Select elements within a rectangle
     * @param {Object} startPos - Starting position in client coordinates {x, y}
     * @param {Object} endPos - Ending position in client coordinates {x, y}
     * @param {boolean} multiSelect - Whether to add to existing selection
     */
    selectElementsInRect(startPos, endPos, multiSelect = false) {
        console.log("Selecting elements in rectangle", { startPos, endPos, multiSelect });

        // Calculate selection rectangle in paper local coordinates
        const localP1 = this.clientToLocalPoint(startPos);
        const localP2 = this.clientToLocalPoint(endPos);

        if (!localP1 || !localP2) {
            console.error("Failed to convert client coordinates to local");
            return;
        }

        // Define the selection rectangle in paper coordinates
        const selectionRect = {
            x: Math.min(localP1.x, localP2.x),
            y: Math.min(localP1.y, localP2.y),
            width: Math.abs(localP2.x - localP1.x),
            height: Math.abs(localP2.y - localP1.y)
        };

        console.log("Selection rectangle in paper coordinates", selectionRect);

        // Find elements within the rectangle
        const elementsInRect = this.graph.getElements().filter(element => {
            if (!element) return false;

            const bbox = element.getBBox();
            if (!bbox) return false;

            // Check if the element's bounding box intersects with the selection rectangle
            return (
                bbox.x < selectionRect.x + selectionRect.width &&
                bbox.x + bbox.width > selectionRect.x &&
                bbox.y < selectionRect.y + selectionRect.height &&
                bbox.y + bbox.height > selectionRect.y
            );
        });

        console.log("Found elements in rectangle:", elementsInRect.length);

        // If not multiSelect, clear existing selection
        if (!multiSelect) {
            this.clearSelection();
        }

        // Add found elements to selection
        elementsInRect.forEach(element => {
            // If multiSelect and already selected, don't add it again
            if (multiSelect && this.selectedElements.some(e => e.id === element.id)) {
                return;
            }

            this.selectedElements.push(element);
            this.highlightElement(element);
        });

        console.log("Selection updated, total elements:", this.selectedElements.length);
    }

    /**
     * Convert client coordinates to paper local coordinates
     * @param {Object} clientPoint - Client coordinates {x, y}
     * @return {Object|null} Paper local coordinates {x, y} or null if error
     */
    clientToLocalPoint(clientPoint) {
        try {
            if (!this.paper || !this.paper.el) return null;

            // If JointJS provides this method, use it
            if (typeof this.paper.clientToLocalPoint === 'function') {
                return this.paper.clientToLocalPoint(clientPoint);
            }

            // Manual conversion as fallback
            const paperRect = this.paper.el.getBoundingClientRect();
            const paperScale = this.paper.scale();
            const paperTranslate = this.paper.translate();

            // Convert client coords to paper container coords
            const offsetX = clientPoint.x - paperRect.left;
            const offsetY = clientPoint.y - paperRect.top;

            // Apply scale and translation to get model coordinates
            return {
                x: (offsetX / paperScale.sx) - paperTranslate.tx,
                y: (offsetY / paperScale.sy) - paperTranslate.ty
            };
        } catch (error) {
            console.error("Error converting coordinates:", error);
            return null;
        }
    }

    /**
     * Select an element
     * @param {Object} element - The element to select
     * @param {boolean} multiSelect - Whether to add to existing selection
     */
    selectElement(element, multiSelect = false) {
        console.log("Selecting element", element.id, "multiSelect:", multiSelect);

        if (!element) return;

        // Check if element exists in graph
        if (!this.graph.getElements().find(el => el.id === element.id)) {
            console.log("Element not found in graph");
            return;
        }

        // For single select, clear previous selection
        if (!multiSelect) {
            this.clearSelection();
        }

        // Check if already selected
        if (this.selectedElements.some(el => el.id === element.id)) {
            if (multiSelect) {
                // If multiSelect, toggle the selection off
                console.log("Element already selected, removing from selection");
                this.unselectElement(element);
            }
            return;
        }

        // Add to selection and highlight
        this.selectedElements.push(element);
        this.highlightElement(element);
        console.log("Element selected, total selection:", this.selectedElements.length);
    }

    /**
     * Unselect a specific element
     * @param {Object} element - The element to unselect
     */
    unselectElement(element) {
        const index = this.selectedElements.findIndex(el => el.id === element.id);
        if (index !== -1) {
            console.log("Unselecting element:", element.id);
            this.unhighlightElement(element);
            this.selectedElements.splice(index, 1);
            console.log("Element unselected, remaining:", this.selectedElements.length);
        }
    }

    /**
     * Clear all selections
     */
    clearSelection() {
        console.log("Clearing all selections, count:", this.selectedElements.length);

        // Make a copy to avoid issues during iteration
        const elements = [...this.selectedElements];

        // Clear the array first to prevent any recursive issues
        this.selectedElements = [];

        // Then unhighlight all elements
        elements.forEach(element => {
            if (element) {
                this.unhighlightElement(element);
            }
        });

        console.log("All selections cleared");
    }

    /**
     * Alias for clearSelection for API compatibility
     */
    clear() {
        this.clearSelection();
    }

    /**
     * Select all elements in the graph
     */
    selectAll() {
        console.log("Selecting all elements");
        this.clearSelection();

        const elements = this.graph.getElements();
        console.log("Found elements:", elements.length);

        elements.forEach(element => {
            if (element) {
                this.selectedElements.push(element);
                this.highlightElement(element);
            }
        });

        console.log("All elements selected, count:", this.selectedElements.length);
    }

    /**
     * Remove selected elements
     */
    removeSelected() {
        if (this.selectedElements.length === 0) return;

        console.log("Removing selected elements, count:", this.selectedElements.length);

        if (confirm(`Delete ${this.selectedElements.length} selected element(s)?`)) {
            const elements = [...this.selectedElements];
            this.selectedElements = []; // Clear first to avoid callbacks issues

            elements.forEach(element => {
                if (element) {
                    console.log("Removing element:", element.id);
                    element.remove();
                }
            });

            console.log("Elements removed");
        }
    }

    /**
     * Highlight an element using the highlighters API
     * @param {Object} element - The element to highlight
     */
    highlightElement(element) {
        if (!element || !element.id) return;

        console.log("Highlighting element:", element.id);
        const view = element.findView(this.paper);

        if (!view) {
            console.log("View not found for element:", element.id);
            return;
        }

        // Use the highlighters API instead of view.highlight
        joint.highlighters.addClass.add(
            view,
            element.isElement() ? 'body' : 'line',
            'selection-highlight',
            { className: 'selection-highlight' }
        );
    }

    /**
     * Unhighlight an element
     * @param {Object} element - The element to unhighlight
     */
    unhighlightElement(element) {
        if (!element || !element.id) return;

        console.log("Unhighlighting element:", element.id);
        const view = element.findView(this.paper);

        if (!view) {
            console.log("View not found for element:", element.id);
            return;
        }

        // Use the highlighters API to remove the highlight
        joint.highlighters.addClass.remove(
            view,
            'selection-highlight'
        );
    }

    /**
     * Set panning mode
     * @param {boolean} isPanning - Whether panning is active
     */
    setPanningMode(isPanning) {
        console.log("Setting panning mode:", isPanning);
        this.isPanning = isPanning;

        // In panning mode, we might want to disable selection
        if (isPanning) {
            this.clearSelection();
        }
    }

    /**
     * Clean up event listeners
     */
    destroy() {
        console.log("Destroying selection manager");

        // Remove all event listeners
        this.eventProxies.forEach(proxy => {
            try {
                if (proxy.target && proxy.event && proxy.handler) {
                    if (proxy.target.off) {
                        proxy.target.off(proxy.event, proxy.handler);
                    } else if (proxy.target.removeEventListener) {
                        proxy.target.removeEventListener(proxy.event, proxy.handler);
                    }
                }
            } catch (e) {
                console.error("Error removing event listener:", e);
            }
        });

        // Clear selections
        this.clearSelection();
        this.removeSelectionBox();

        // Remove style element if it exists
        if (this.styleElement && this.styleElement.parentNode) {
            this.styleElement.parentNode.removeChild(this.styleElement);
        }

        this.eventProxies = [];

        console.log("Selection manager destroyed");
    }
}

// Function to register selection with panning mode
function registerSelectionWithPanMode(selection, panButton) {
    if (!selection || !panButton) {
        console.log("Cannot register selection with pan mode: missing parameters");
        return;
    }

    console.log("Registering selection with pan mode");
    const originalClickHandler = panButton.onclick;

    panButton.onclick = function(event) {
        // Call the original handler if it exists
        if (originalClickHandler) {
            originalClickHandler.call(this, event);
        }

        // Update the Selection instance's panning state
        const isPanning = this.textContent === 'Selection Mode';
        console.log("Pan button clicked, setting panning mode:", isPanning);
        selection.setPanningMode(isPanning);
    };
}
