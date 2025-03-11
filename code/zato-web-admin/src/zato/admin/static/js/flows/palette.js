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
                    return; // If no matching type, exit the function
            }

            if (!element) return;

            // Calculate a safe position within the paper
            var paperEl = paper.el;
            var paperRect = paperEl.getBoundingClientRect();

            // Make sure we have valid dimensions
            var paperWidth = paperRect.width || 1000;
            var paperHeight = paperRect.height || 800;

            // Calculate a position within the visible area of the paper
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
