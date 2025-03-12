// selection_rubber_band.js - Rubber-band selection functionality

/**
 * Enhances the Selection class with rubber-band (marquee) selection functionality.
 * This module extends the core Selection class with the ability to select multiple
 * elements by dragging to create a selection rectangle.
 */

/**
 * Initialize rubber-band selection for a Selection instance
 * @param {Selection} selection - The Selection instance to enhance
 */
 function initRubberBandSelection(selection) {
    // Rubber-band selection state
    selection.selectionBox = null;
    selection.selectionStartPosition = null;
    selection.isSelecting = false;
    selection.hasMovedDuringSelection = false;

    // Add CSS style for selection box
    const color = "#2196F3";
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        .selection-box {
            position: absolute;
            border: 2px dashed ${color};
            background-color: rgba(33, 150, 243, 0.1);
            pointer-events: none;
            z-index: 1000;
        }
    `;
    document.head.appendChild(styleElement);
    selection.rubberBandStyleElement = styleElement;

    // Set up event handlers for rubber-band selection
    setupRubberBandEvents(selection);

    console.log("Rubber-band selection initialized");
}

/**
 * Set up the event listeners for rubber-band selection
 * @param {Selection} selection - The Selection instance
 */
function setupRubberBandEvents(selection) {
    // Start rubber-band selection
    const handleBlankPointerDown = (evt, x, y) => {
        // Only start selection if not in panning mode
        if (selection.isPanning) return;

        console.log("Starting rubber-band selection at", x, y);
        selection.isSelecting = true;
        selection.hasMovedDuringSelection = false;

        // Store actual client coordinates
        selection.selectionStartPosition = {
            x: evt.clientX,
            y: evt.clientY
        };

        // Create selection box element
        createSelectionBox(selection);

        // If not using modifier keys, clear the current selection
        if (!(evt.ctrlKey || evt.shiftKey)) {
            selection.clearSelection();
        }
    };

    // Update rubber-band selection
    const handleMouseMove = (evt) => {
        if (!selection.isSelecting) return;

        // Get current client position
        const currentPosition = {
            x: evt.clientX,
            y: evt.clientY
        };

        // Check if we've moved enough to count as a drag
        const moveThreshold = 5;
        if (!selection.hasMovedDuringSelection) {
            const dx = Math.abs(currentPosition.x - selection.selectionStartPosition.x);
            const dy = Math.abs(currentPosition.y - selection.selectionStartPosition.y);
            if (dx > moveThreshold || dy > moveThreshold) {
                selection.hasMovedDuringSelection = true;
            }
        }

        // Update selection box
        updateSelectionBox(selection, selection.selectionStartPosition, currentPosition);
    };

    // Complete rubber-band selection
    const handleMouseUp = (evt) => {
        if (!selection.isSelecting) return;

        console.log("Completing rubber-band selection");
        selection.isSelecting = false;

        // If we actually dragged to create a selection box
        if (selection.hasMovedDuringSelection) {
            // Get current client position
            const endPosition = {
                x: evt.clientX,
                y: evt.clientY
            };

            // Select elements within the rectangle
            selectElementsInRect(
                selection,
                selection.selectionStartPosition,
                endPosition,
                evt.ctrlKey || evt.shiftKey
            );
        }

        // Clean up
        removeSelectionBox(selection);
        selection.selectionStartPosition = null;
    };

    // Register event handlers
    selection.paper.on('blank:pointerdown', handleBlankPointerDown);
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    // Add to proxies for cleanup
    selection.eventProxies.push(
        { target: selection.paper, event: 'blank:pointerdown', handler: handleBlankPointerDown },
        { target: document, event: 'mousemove', handler: handleMouseMove },
        { target: document, event: 'mouseup', handler: handleMouseUp }
    );

    console.log("Rubber-band selection event listeners set up");
}

/**
 * Create a selection box for rubber-band selection
 * @param {Selection} selection - The Selection instance
 */
function createSelectionBox(selection) {
    // Remove any existing selection box
    removeSelectionBox(selection);

    // Create a new selection box
    selection.selectionBox = document.createElement('div');
    selection.selectionBox.className = 'selection-box';

    // Critical: Ensure the box uses absolute positioning
    selection.selectionBox.style.position = 'absolute';

    // Get the paper element and its parent
    const paperEl = selection.paper.el;

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
        container.appendChild(selection.selectionBox);
    } else {
        // Fallback to paper's parent
        if (paperEl.parentNode) {
            paperEl.parentNode.appendChild(selection.selectionBox);
        }
    }

    // Initially hidden
    selection.selectionBox.style.display = 'none';
}

/**
 * Update the selection box dimensions
 * @param {Selection} selection - The Selection instance
 * @param {Object} startPos - Starting position in client coordinates {x, y}
 * @param {Object} endPos - Current position in client coordinates {x, y}
 */
function updateSelectionBox(selection, startPos, endPos) {
    if (!selection.selectionBox) return;

    // Get the paper element position
    const paperRect = selection.paper.el.getBoundingClientRect();

    // Get the container element position (the selection box's parent)
    const containerRect = selection.selectionBox.parentNode.getBoundingClientRect();

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
    selection.selectionBox.style.left = `${left}px`;
    selection.selectionBox.style.top = `${top}px`;
    selection.selectionBox.style.width = `${width}px`;
    selection.selectionBox.style.height = `${height}px`;
    selection.selectionBox.style.display = 'block';
}

/**
 * Remove the selection box
 * @param {Selection} selection - The Selection instance
 */
function removeSelectionBox(selection) {
    if (selection.selectionBox && selection.selectionBox.parentNode) {
        selection.selectionBox.parentNode.removeChild(selection.selectionBox);
        selection.selectionBox = null;
    }
}

/**
 * Select elements within a rectangle
 * @param {Selection} selection - The Selection instance
 * @param {Object} startPos - Starting position in client coordinates {x, y}
 * @param {Object} endPos - Ending position in client coordinates {x, y}
 * @param {boolean} multiSelect - Whether to add to existing selection
 */
function selectElementsInRect(selection, startPos, endPos, multiSelect = false) {
    console.log("Selecting elements in rectangle", { startPos, endPos, multiSelect });

    // Calculate selection rectangle in paper local coordinates
    const localP1 = clientToLocalPoint(selection, startPos);
    const localP2 = clientToLocalPoint(selection, endPos);

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
    const elementsInRect = selection.graph.getElements().filter(element => {
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
        selection.clearSelection();
    }

    // Add found elements to selection
    elementsInRect.forEach(element => {
        // If multiSelect and already selected, don't add it again
        if (multiSelect && selection.selectedElements.some(e => e.id === element.id)) {
            return;
        }

        selection.selectedElements.push(element);
        selection.highlightElement(element);
    });

    console.log("Selection updated, total elements:", selection.selectedElements.length);
}

/**
 * Convert client coordinates to paper local coordinates
 * @param {Selection} selection - The Selection instance
 * @param {Object} clientPoint - Client coordinates {x, y}
 * @return {Object|null} Paper local coordinates {x, y} or null if error
 */
function clientToLocalPoint(selection, clientPoint) {
    try {
        if (!selection.paper || !selection.paper.el) return null;

        // If JointJS provides this method, use it
        if (typeof selection.paper.clientToLocalPoint === 'function') {
            return selection.paper.clientToLocalPoint(clientPoint);
        }

        // Manual conversion as fallback
        const paperRect = selection.paper.el.getBoundingClientRect();
        const paperScale = selection.paper.scale();
        const paperTranslate = selection.paper.translate();

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
 * Clean up rubber-band selection resources
 * @param {Selection} selection - The Selection instance
 */
function cleanupRubberBandSelection(selection) {
    // Remove selection box
    removeSelectionBox(selection);

    // Remove the rubber-band specific style element
    if (selection.rubberBandStyleElement && selection.rubberBandStyleElement.parentNode) {
        selection.rubberBandStyleElement.parentNode.removeChild(selection.rubberBandStyleElement);
    }
}

// Export functions for integration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initRubberBandSelection,
        cleanupRubberBandSelection
    };
}
