// palette.js - Draggable palette functionality with both click and drag support

function setupDraggablePalette(graph, paper) {
    if (!graph || !paper) {
        console.error("Graph or paper object not provided to setupDraggablePalette");
        return;
    }

    // Make palette items draggable
    var paletteItems = document.querySelectorAll('.palette-item');

    if (!paletteItems.length) {
        console.warn("No palette items found to make draggable");
        return;
    }

    // Variables to track dragging state
    let isDragging = false;
    let dragStartX = 0;
    let dragStartY = 0;
    let dragGhost = null;
    let dragType = null;

    // Function to create element based on type
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

    // Add element to center of paper
    function addElementToCenter() {
        try {
            // Get the paper dimensions
            const paperRect = paper.el.getBoundingClientRect();
            const paperWidth = paperRect.width || 1000;
            const paperHeight = paperRect.height || 800;

            // Calculate center position
            const centerX = paperWidth / 2;
            const centerY = paperHeight / 2;

            // Get paper coordinates
            let paperPoint = clientToPaperPoint(
                paperRect.left + centerX,
                paperRect.top + centerY
            );

            return paperPoint;
        } catch (error) {
            console.error("Error calculating center position:", error);
            return { x: 100, y: 100 }; // Fallback position
        }
    }

    // Convert client coordinates to paper coordinates
    function clientToPaperPoint(clientX, clientY) {
        try {
            const paperRect = paper.el.getBoundingClientRect();
            const scale = paper.scale();
            const translate = paper.translate();

            // Calculate position in scaled/translated paper coordinate system
            const localX = clientX - paperRect.left;
            const localY = clientY - paperRect.top;

            return {
                x: (localX / scale.sx) - translate.tx,
                y: (localY / scale.sy) - translate.ty
            };
        } catch (error) {
            console.error("Error converting coordinates:", error);
            return { x: 0, y: 0 };
        }
    }

    // Create a ghost element for drag visual
    function createDragGhost(item, x, y) {
        const ghost = document.createElement('div');
        ghost.className = 'drag-ghost';
        ghost.textContent = item.textContent;
        ghost.style.position = 'fixed';
        ghost.style.left = (x + 10) + 'px'; // Offset from cursor
        ghost.style.top = (y + 10) + 'px';
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

    // Add element at specified position
    function addElementAtPosition(element, x, y) {
        try {
            // Adjust position to center the element
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

    // Process each palette item
    paletteItems.forEach(function(item) {
        // Click handler - add element to center of paper
        item.addEventListener('click', function(event) {
            // Only handle as click if we're not dragging
            if (isDragging) return;

            try {
                const type = this.getAttribute('data-type');
                if (!type) {
                    console.warn("No element type found for palette item");
                    return;
                }

                const element = createElementByType(type);
                if (!element) return;

                // Add to center of paper
                const center = addElementToCenter();
                addElementAtPosition(element, center.x, center.y);

                console.log('Element added via click at center');
            } catch (error) {
                console.error("Error processing click:", error);
            }
        });

        // Mouse down - start potential drag
        item.addEventListener('mousedown', function(event) {
            // Initialize drag variables
            dragStartX = event.clientX;
            dragStartY = event.clientY;
            dragType = this.getAttribute('data-type');

            // Prevent text selection
            event.preventDefault();

            // Set up document level handlers for drag operation
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

        item.addEventListener('mousedown', function() {
            this.style.backgroundColor = '#d9d9d9';
        });

        item.addEventListener('mouseup', function() {
            this.style.backgroundColor = '#e9e9e9';
        });
    });

    // Handle mouse movement during drag
    function handleMouseMove(event) {
        // Check if we've moved enough to consider it a drag
        const moveThreshold = 5;
        const dx = Math.abs(event.clientX - dragStartX);
        const dy = Math.abs(event.clientY - dragStartY);

        // If we've moved beyond threshold, start dragging
        if (!isDragging && (dx > moveThreshold || dy > moveThreshold)) {
            isDragging = true;

            // Find the palette item to create ghost
            const item = document.querySelector(`.palette-item[data-type="${dragType}"]`);
            if (item) {
                dragGhost = createDragGhost(item, event.clientX, event.clientY);
            }
        }

        // If dragging, move the ghost
        if (isDragging && dragGhost) {
            dragGhost.style.left = (event.clientX + 10) + 'px';
            dragGhost.style.top = (event.clientY + 10) + 'px';
        }
    }

    // Handle mouse up to complete drag or click
    function handleMouseUp(event) {
        try {
            // Only process if we were dragging
            if (isDragging && dragGhost) {
                // Check if we're over the paper
                const paperRect = paper.el.getBoundingClientRect();
                if (
                    event.clientX >= paperRect.left &&
                    event.clientX <= paperRect.right &&
                    event.clientY >= paperRect.top &&
                    event.clientY <= paperRect.bottom
                ) {
                    // Create the element
                    const element = createElementByType(dragType);
                    if (element) {
                        // Get paper coordinates for drop position
                        const paperPos = clientToPaperPoint(event.clientX, event.clientY);

                        // Add element at drop position
                        addElementAtPosition(element, paperPos.x, paperPos.y);
                    }
                }
            }
        } catch (error) {
            console.error("Error handling mouse up:", error);
        } finally {
            // Clean up
            if (dragGhost && dragGhost.parentNode) {
                dragGhost.parentNode.removeChild(dragGhost);
            }

            dragGhost = null;
            isDragging = false;

            // Remove event listeners
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        }
    }

    console.log("Palette setup complete with both click and drag support");
}
