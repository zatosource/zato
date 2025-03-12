// selection_group_operations.js - Group operations for selections

/**
 * Enhances the Selection class with group operations functionality.
 * This module extends the core Selection class with the ability to
 * manipulate multiple selected elements as a group, most importantly
 * for moving multiple elements together.
 */

/**
 * Initialize group operations for a Selection instance
 * @param {Selection} selection - The Selection instance to enhance
 */
 function initGroupOperations(selection) {
    // Group movement tracking variables
    selection.dragStartPositions = {};
    selection.isDragging = false;
    selection.draggedElement = null;

    // Set up event handlers for group operations
    setupGroupOperationEvents(selection);

    console.log("Group operations initialized");
}

/**
 * Set up the event listeners for group operations
 * @param {Selection} selection - The Selection instance
 */
function setupGroupOperationEvents(selection) {
    // Group movement: Handle element drag start
    const handleElementPointerDown = (elementView, evt) => {
        if (selection.isPanning) return; // Don't track dragging in panning mode

        const element = elementView.model;
        // Check if the element is in the selection
        if (selection.selectedElements.some(el => el.id === element.id)) {
            console.log("Starting group drag with element:", element.id);
            selection.isDragging = true;
            selection.draggedElement = element;

            // Store initial positions of all selected elements
            selection.dragStartPositions = {};
            selection.selectedElements.forEach(el => {
                const position = el.position();
                if (position) {
                    selection.dragStartPositions[el.id] = { ...position }; // Clone to avoid reference issues
                }
            });
        }
    };

    // Group movement: Handle element drag move
    const handleElementPointermove = (elementView, evt, x, y) => {
        // Only handle if we're dragging a selected element
        if (!selection.isDragging || !selection.draggedElement) return;

        // Don't move elements in panning mode
        if (selection.isPanning) return;

        // Get the dragged element's new position
        const draggedElementId = selection.draggedElement.id;
        const newPosition = selection.draggedElement.position();
        const startPosition = selection.dragStartPositions[draggedElementId];

        if (!startPosition || !newPosition) return;

        // Calculate movement delta
        const dx = newPosition.x - startPosition.x;
        const dy = newPosition.y - startPosition.y;

        // Move all other selected elements by the same delta
        selection.selectedElements.forEach(el => {
            if (el.id !== draggedElementId) {
                const elStartPos = selection.dragStartPositions[el.id];
                // Skip if we don't have a starting position
                if (!elStartPos) return;

                // Move the element to its new position
                el.position(elStartPos.x + dx, elStartPos.y + dy);
            }
        });
    };

    // Group movement: Handle element drag end
    const handleElementPointerUp = (elementView, evt) => {
        if (selection.isDragging) {
            console.log("Ending group drag");
            selection.isDragging = false;
            selection.draggedElement = null;
            selection.dragStartPositions = {};
        }
    };

    // Register group operation event handlers
    selection.paper.on('element:pointerdown', handleElementPointerDown);
    selection.paper.on('element:pointermove', handleElementPointermove);
    selection.paper.on('element:pointerup', handleElementPointerUp);

    // Add to proxies for cleanup
    selection.eventProxies.push(
        { target: selection.paper, event: 'element:pointerdown', handler: handleElementPointerDown },
        { target: selection.paper, event: 'element:pointermove', handler: handleElementPointermove },
        { target: selection.paper, event: 'element:pointerup', handler: handleElementPointerUp }
    );

    console.log("Group operations event listeners set up");
}

/**
 * Duplicate selected elements
 * @param {Selection} selection - The Selection instance
 * @param {number} offsetX - Horizontal offset for duplicated elements
 * @param {number} offsetY - Vertical offset for duplicated elements
 */
function duplicateSelected(selection, offsetX = 20, offsetY = 20) {
    if (selection.selectedElements.length === 0) return;

    console.log("Duplicating selected elements, count:", selection.selectedElements.length);

    // Make a copy to avoid issues during iteration
    const elementsToClone = [...selection.selectedElements];

    // Clear current selection before adding duplicates
    selection.clearSelection();

    // Store newly created elements
    const newElements = [];

    // Clone each selected element
    elementsToClone.forEach(element => {
        try {
            if (element && element.clone) {
                // Clone the element
                const clone = element.clone();

                // Get position and offset it
                const position = element.position();
                if (position) {
                    clone.position(position.x + offsetX, position.y + offsetY);
                }

                // Add to graph and selection
                selection.graph.addCell(clone);
                newElements.push(clone);
            }
        } catch (error) {
            console.error("Error cloning element:", error);
        }
    });

    // Select all the new elements
    newElements.forEach(element => {
        selection.selectElement(element, true);
    });

    console.log("Elements duplicated and selected, count:", newElements.length);
}

/**
 * Align selected elements horizontally
 * @param {Selection} selection - The Selection instance
 * @param {string} alignment - Alignment type: 'left', 'center', 'right'
 */
function alignHorizontally(selection, alignment = 'center') {
    if (selection.selectedElements.length <= 1) return;

    console.log(`Aligning ${selection.selectedElements.length} elements horizontally: ${alignment}`);

    let targetX;

    // Determine target X coordinate based on alignment type
    switch (alignment) {
        case 'left': {
            // Find leftmost element
            targetX = Math.min(...selection.selectedElements.map(el => {
                const pos = el.position();
                return pos ? pos.x : Infinity;
            }));
            break;
        }
        case 'right': {
            // Find rightmost edge
            targetX = Math.max(...selection.selectedElements.map(el => {
                const pos = el.position();
                const size = el.size();
                return pos && size ? pos.x + size.width : -Infinity;
            }));
            // Adjust for element width
            selection.selectedElements.forEach(el => {
                const size = el.size();
                if (!size) return;
                const pos = el.position();
                if (pos) {
                    el.position(targetX - size.width, pos.y);
                }
            });
            return; // Early return since we handled positioning
        }
        case 'center':
        default: {
            // Find center of all elements
            const bounds = getSelectionBounds(selection);
            if (!bounds) return;

            targetX = bounds.x + (bounds.width / 2);

            // Position elements centered around the target X
            selection.selectedElements.forEach(el => {
                const size = el.size();
                if (!size) return;
                const pos = el.position();
                if (pos) {
                    el.position(targetX - (size.width / 2), pos.y);
                }
            });
            return; // Early return since we handled positioning
        }
    }

    // For left alignment or fallback
    selection.selectedElements.forEach(el => {
        const pos = el.position();
        if (pos) {
            el.position(targetX, pos.y);
        }
    });
}

/**
 * Align selected elements vertically
 * @param {Selection} selection - The Selection instance
 * @param {string} alignment - Alignment type: 'top', 'middle', 'bottom'
 */
function alignVertically(selection, alignment = 'middle') {
    if (selection.selectedElements.length <= 1) return;

    console.log(`Aligning ${selection.selectedElements.length} elements vertically: ${alignment}`);

    let targetY;

    // Determine target Y coordinate based on alignment type
    switch (alignment) {
        case 'top': {
            // Find topmost element
            targetY = Math.min(...selection.selectedElements.map(el => {
                const pos = el.position();
                return pos ? pos.y : Infinity;
            }));
            break;
        }
        case 'bottom': {
            // Find bottommost edge
            targetY = Math.max(...selection.selectedElements.map(el => {
                const pos = el.position();
                const size = el.size();
                return pos && size ? pos.y + size.height : -Infinity;
            }));
            // Adjust for element height
            selection.selectedElements.forEach(el => {
                const size = el.size();
                if (!size) return;
                const pos = el.position();
                if (pos) {
                    el.position(pos.x, targetY - size.height);
                }
            });
            return; // Early return since we handled positioning
        }
        case 'middle':
        default: {
            // Find middle of all elements
            const bounds = getSelectionBounds(selection);
            if (!bounds) return;

            targetY = bounds.y + (bounds.height / 2);

            // Position elements centered around the target Y
            selection.selectedElements.forEach(el => {
                const size = el.size();
                if (!size) return;
                const pos = el.position();
                if (pos) {
                    el.position(pos.x, targetY - (size.height / 2));
                }
            });
            return; // Early return since we handled positioning
        }
    }

    // For top alignment or fallback
    selection.selectedElements.forEach(el => {
        const pos = el.position();
        if (pos) {
            el.position(pos.x, targetY);
        }
    });
}

/**
 * Get the bounding rectangle of all selected elements
 * @param {Selection} selection - The Selection instance
 * @return {Object|null} The bounding rectangle or null if no elements are selected
 */
function getSelectionBounds(selection) {
    if (selection.selectedElements.length === 0) return null;

    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;

    selection.selectedElements.forEach(el => {
        const pos = el.position();
        const size = el.size();

        if (!pos || !size) return;

        minX = Math.min(minX, pos.x);
        minY = Math.min(minY, pos.y);
        maxX = Math.max(maxX, pos.x + size.width);
        maxY = Math.max(maxY, pos.y + size.height);
    });

    return {
        x: minX,
        y: minY,
        width: maxX - minX,
        height: maxY - minY
    };
}

/**
 * Distribute selected elements horizontally with equal spacing
 * @param {Selection} selection - The Selection instance
 */
function distributeHorizontally(selection) {
    if (selection.selectedElements.length <= 2) return;

    console.log(`Distributing ${selection.selectedElements.length} elements horizontally`);

    // Get elements sorted by x position
    const elements = [...selection.selectedElements].sort((a, b) => {
        const posA = a.position();
        const posB = b.position();
        return posA && posB ? posA.x - posB.x : 0;
    });

    // Get leftmost and rightmost positions
    const firstElement = elements[0];
    const lastElement = elements[elements.length - 1];

    const firstPos = firstElement.position();
    const lastPos = lastElement.position();
    const lastSize = lastElement.size();

    if (!firstPos || !lastPos || !lastSize) return;

    // Calculate total available space
    const startX = firstPos.x;
    const endX = lastPos.x + lastSize.width;
    const totalWidth = endX - startX;

    // Calculate spacing between elements
    const spacing = totalWidth / (elements.length - 1);

    // Position each element (except first and last)
    for (let i = 1; i < elements.length - 1; i++) {
        const element = elements[i];
        const pos = element.position();
        const size = element.size();

        if (!pos || !size) continue;

        const newX = startX + (spacing * i) - (size.width / 2);
        element.position(newX, pos.y);
    }
}

/**
 * Distribute selected elements vertically with equal spacing
 * @param {Selection} selection - The Selection instance
 */
function distributeVertically(selection) {
    if (selection.selectedElements.length <= 2) return;

    console.log(`Distributing ${selection.selectedElements.length} elements vertically`);

    // Get elements sorted by y position
    const elements = [...selection.selectedElements].sort((a, b) => {
        const posA = a.position();
        const posB = b.position();
        return posA && posB ? posA.y - posB.y : 0;
    });

    // Get topmost and bottommost positions
    const firstElement = elements[0];
    const lastElement = elements[elements.length - 1];

    const firstPos = firstElement.position();
    const lastPos = lastElement.position();
    const lastSize = lastElement.size();

    if (!firstPos || !lastPos || !lastSize) return;

    // Calculate total available space
    const startY = firstPos.y;
    const endY = lastPos.y + lastSize.height;
    const totalHeight = endY - startY;

    // Calculate spacing between elements
    const spacing = totalHeight / (elements.length - 1);

    // Position each element (except first and last)
    for (let i = 1; i < elements.length - 1; i++) {
        const element = elements[i];
        const pos = element.position();
        const size = element.size();

        if (!pos || !size) continue;

        const newY = startY + (spacing * i) - (size.height / 2);
        element.position(pos.x, newY);
    }
}

/**
 * Clean up group operations resources
 * @param {Selection} selection - The Selection instance
 */
function cleanupGroupOperations(selection) {
    // Reset group operation state
    selection.isDragging = false;
    selection.draggedElement = null;
    selection.dragStartPositions = {};
}

// Export functions for integration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initGroupOperations,
        duplicateSelected,
        alignHorizontally,
        alignVertically,
        distributeHorizontally,
        distributeVertically,
        cleanupGroupOperations
    };
}
