// palette.js - Enhanced palette with both click and drag-drop functionality

function setupDraggablePalette(graph, paper) {
    if (!graph || !paper) {
        console.error("Graph or paper object not provided to setupDraggablePalette");
        return;
    }

    // Make palette items draggable
    const paletteItems = document.querySelectorAll('.palette-item');

    if (!paletteItems.length) {
        console.warn("No palette items found to make draggable");
        return;
    }

    // Track drag state
    let isDragging = false;
    let dragElement = null;
    let dragGhost = null;
    let dragStartX = 0;
    let dragStartY = 0;

    // Create element based on type
    function createElementByType(type) {
        let element;
        switch (type) {
            case 'start':
                element = new joint.shapes.workflow.Start();
                break;
            case 'stop':
                element = new joint.shapes.workflow.Stop();
                break;
            case 'service':
                element = new joint.shapes.workflow.Service();
                break;
            case 'parallel':
                element = new joint.shapes.workflow.Parallel();
                break;
            case 'forkjoin':
                element = new joint.shapes.workflow.ForkJoin();
                break;
            default:
                console.warn("Unknown element type:", type);
                return null;
        }
        return element;
    }

    // Convert client coordinates to paper coordinates
    function clientToPaperCoordinates(clientX, clientY) {
        const paperRect = paper.el.getBoundingClientRect();
        const localPoint = {
            x: clientX - paperRect.left,
            y: clientY - paperRect.top
        };

        // Account for paper scale and translation
        const scale = paper.scale();
        const translate = paper.translate();

        return {
            x: (localPoint.x / scale.sx) - translate.tx,
            y: (localPoint.y / scale.sy) - translate.ty
        };
    }

    // Create a ghost element for drag visual
    function createDragGhost(element, x, y) {
        const ghost = document.createElement('div');
        ghost.className = 'drag-ghost';
        ghost.textContent = element.textContent;
        ghost.style.position = 'fixed';
        ghost.style.left = x + 'px';
        ghost.style.top = y + 'px';
        ghost.style.backgroundColor = '#f5f5f5';
        ghost.style.border = '1px solid #ccc';
        ghost.style.padding = '8px';
        ghost.style.borderRadius = '4px';
        ghost.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
        ghost.style.opacity = '0.8';
        ghost.style.zIndex = '9999';
        ghost.style.pointerEvents = 'none'; // Allow events to pass through
        document.body.appendChild(ghost);
        return ghost;
    }

    // Add center element at specific position
    function addElementAtPosition(element, x, y) {
        try {
            if (!element) return;

            // Center the element on the cursor
            const size = element.get('size');
            const position = {
                x: x - (size.width / 2),
                y: y - (size.height / 2)
            };

            // Make sure position is valid
            if (isNaN(position.x) || isNaN(position.y)) {
                console.warn("Invalid position calculated, using fallback");
                position.x = 100;
                position.y = 100;
            }

            // Position the element and add to graph
            element.position(position.x, position.y);
            graph.addCell(element);

            console.log('Element added at position:', position);
        } catch (error) {
            console.error("Error adding element at position:", error);
        }
    }

    // Clean up drag operations
    function cleanupDrag() {
        if (dragGhost && dragGhost.parentNode) {
            dragGhost.parentNode.removeChild(dragGhost);
        }
        isDragging = false;
        dragElement = null;
        dragGhost = null;
    }

    // Handle clicks - adds element at center of paper
    paletteItems.forEach(function(item) {
        // Click handler - for the existing behavior
        item.addEventListener('click', function(event) {
            // Skip if we're ending a drag operation
            if (isDragging) return;

            try {
                const type = this.getAttribute('data-type');
                if (!type) {
                    console.warn("No element type found for palette item");
                    return;
                }

                const element = createElementByType(type);
                if (!element) return;

                // Get the paper dimensions
                const paperEl = paper.el;
                const paperRect = paperEl.getBoundingClientRect();
                const paperWidth = paperRect.width || 1000;
                const paperHeight = paperRect.height || 800;

                // Calculate center position of the visible paper area
                const viewportCenterX = paperWidth / 2;
                const viewportCenterY = paperHeight / 2;

                // Convert to paper coordinates
                const paperPos = clientToPaperCoordinates(
                    paperRect.left + viewportCenterX,
                    paperRect.top + viewportCenterY
                );

                // Add the element to the graph
                addElementAtPosition(element, paperPos.x, paperPos.y);
            } catch (error) {
                console.error("Error adding element from palette:", error);
            }
        });

        // Mousedown handler - for starting drag operations
        item.addEventListener('mousedown', function(event) {
            // Prevent text selection during drag
            event.preventDefault();

            const type = this.getAttribute('data-type');
            if (!type) return;

            // Store the element type for use in mousemove/mouseup
            dragElement = type;
            dragStartX = event.clientX;
            dragStartY = event.clientY;

            // Create the visual ghost element for dragging
            dragGhost = createDragGhost(this, dragStartX, dragStartY);

            // Track drag state
            isDragging = true;

            // Add document-level event listeners
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
        });

        // Visual feedback
        item.addEventListener('mouseover', function() {
            this.style.backgroundColor = '#e9e9e9';
            this.style.cursor = 'grab';
        });

        item.addEventListener('mouseout', function() {
            this.style.backgroundColor = '';
            this.style.cursor = '';
        });
    });

    // Handle mouse movement during drag
    function handleMouseMove(event) {
        if (!isDragging || !dragGhost) return;

        // Move the ghost with the cursor
        dragGhost.style.left = event.clientX + 'px';
        dragGhost.style.top = event.clientY + 'px';
    }

    // Handle mouse up to complete drag operation
    function handleMouseUp(event) {
        if (!isDragging) return;

        try {
            // Check if we're over the paper
            const paperRect = paper.el.getBoundingClientRect();
            if (
                event.clientX >= paperRect.left &&
                event.clientX <= paperRect.right &&
                event.clientY >= paperRect.top &&
                event.clientY <= paperRect.bottom
            ) {
                // Create the actual element
                const element = createElementByType(dragElement);
                if (element) {
                    // Get paper coordinates for the drop position
                    const paperPos = clientToPaperCoordinates(event.clientX, event.clientY);

                    // Add the element at the drop position
                    addElementAtPosition(element, paperPos.x, paperPos.y);
                }
            }
        } catch (error) {
            console.error("Error completing drag operation:", error);
        } finally {
            // Clean up
            cleanupDrag();

            // Remove document event listeners
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        }
    }

    console.log("Enhanced palette setup complete. Items can be clicked or dragged.");
}
