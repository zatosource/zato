// palette.js - Simplified and robust draggable palette functionality

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

    // Main click handler for each palette item
    paletteItems.forEach(function(item) {
        item.addEventListener('click', function(event) {
            try {
                // Get the element type from data-type attribute
                const type = this.getAttribute('data-type');

                if (!type) {
                    console.warn("No element type found for palette item");
                    return;
                }

                // Create element based on type
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
                        return;
                }

                if (!element) {
                    console.warn("Failed to create element of type:", type);
                    return;
                }

                // Get the paper dimensions
                const paperEl = paper.el;
                const paperRect = paperEl.getBoundingClientRect();
                const paperWidth = paperRect.width || 1000;
                const paperHeight = paperRect.height || 800;

                // Calculate a sensible position - in the center of the visible paper
                // Get the current scroll position and paper translation
                const scrollLeft = paperEl.scrollLeft || 0;
                const scrollTop = paperEl.scrollTop || 0;
                const translate = paper.translate();
                const scale = paper.scale();

                // Calculate a position in the center of the viewport
                const viewportCenterX = paperWidth / 2;
                const viewportCenterY = paperHeight / 2;

                // Adjust for paper's transformation
                const position = {
                    x: (viewportCenterX / scale.sx) - translate.tx,
                    y: (viewportCenterY / scale.sy) - translate.ty
                };

                // Center the element at the position
                const size = element.get('size');
                position.x -= size.width / 2;
                position.y -= size.height / 2;

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
                console.error("Error adding element from palette:", error);
                alert("Error adding element. See console for details.");
            }
        });

        // Visual feedback for better UX
        item.addEventListener('mouseover', function() {
            this.style.backgroundColor = '#e9e9e9';
            this.style.cursor = 'pointer';
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

    console.log("Palette setup complete. Items should be clickable.");
}
