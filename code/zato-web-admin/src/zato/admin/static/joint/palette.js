// palette.js - Draggable palette functionality

function setupDraggablePalette(graph, paper) {
    // Make palette items draggable
    var paletteItems = document.querySelectorAll('.palette-item');

    paletteItems.forEach(function(item) {
        item.addEventListener('mousedown', function(event) {
            var type = event.target.getAttribute('data-type');
            var element;

            // Create a new element based on the type
            switch (type) {
                case 'task':
                    element = new joint.shapes.workflow.Task();
                    break;
                case 'process':
                    element = new joint.shapes.workflow.Process();
                    break;
                case 'decision':
                    element = new joint.shapes.workflow.Decision();
                    break;
                case 'start':
                    element = new joint.shapes.workflow.Start();
                    break;
                case 'end':
                    element = new joint.shapes.workflow.End();
                    break;
                case 'timer':
                    element = new joint.shapes.workflow.Timer();
                    break;
                case 'link':
                    // Enable link drawing mode
                    paper.setInteractivity({ linkMove: true });
                    paper.options.defaultLink = new joint.shapes.standard.Link({
                        attrs: {
                            line: {
                                stroke: '#333333',
                                strokeWidth: 2,
                                targetMarker: {
                                    type: 'path',
                                    d: 'M 10 -5 0 0 10 5 z'
                                }
                            }
                        },
                        router: { name: 'manhattan' },
                        connector: { name: 'rounded' }
                    });

                    // Set interactive flag for creating links
                    paper.options.interactive = { linkPinning: false };
                    paper.options.interactive.addLinkFromMagnet = true;
                    return;
            }

            if (!element) return;

            // Calculate a safe position within the paper
            var paperEl = paper.el;
            var paperRect = paperEl.getBoundingClientRect();

            // Make sure we have valid dimensions
            var paperWidth = paperRect.width || 1000;
            var paperHeight = paperRect.height || 800;

            // Calculate a position within the visible area of the paper
            // Use specific values rather than random to avoid NaN issues
            var position = {
                x: Math.max(100, Math.min(paperWidth - 150, paperWidth / 2)),
                y: Math.max(100, Math.min(paperHeight - 150, paperHeight / 2))
            };

            // Position the element and add to graph
            element.position(position.x, position.y);
            graph.addCell(element);

            console.log('Element added at position:', position);
        });
    });
}
