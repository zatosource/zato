// main.js - Main application initialization and setup

document.addEventListener('DOMContentLoaded', function() {
    // Initialize workflow editor
    var graph = new joint.dia.Graph();

    var paper = new joint.dia.Paper({
        el: document.getElementById('paper'),
        model: graph,
        width: '100%',
        height: '100%',
        gridSize: 10,
        drawGrid: true,
        background: {
            color: 'rgba(0, 0, 0, 0.05)'
        },
        defaultLink: new joint.shapes.standard.Link({
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
        }),
        highlighting: {
            default: {
                name: 'stroke',
                options: {
                    padding: 6,
                    attrs: {
                        'stroke-width': 3,
                        stroke: '#4666E5'
                    }
                }
            }
        },
        interactive: {
            linkMove: true,
            elementMove: true,
            arrowheadMove: true
        }
    });

    // Enhance the paper's interactive settings for better snapping behavior
    paper.options.snapLinks = {
        radius: 20  // The distance within which a link end will snap to a magnet
    };

    paper.options.validateConnection = function(sourceView, sourceMagnet, targetView, targetMagnet) {
        // You can add custom validation logic here if needed
        return targetMagnet != null; // Only allow connections to magnets/ports
    };

    // Create Selection instance
    var selection = new Selection(graph, paper);

    // Pan mode
    var isPanning = false;
    var panButton = document.getElementById('pan-paper');

    panButton.addEventListener('click', function() {
        isPanning = !isPanning;
        if (isPanning) {
            this.textContent = 'Selection Mode';
            paper.setInteractivity(false);
        } else {
            this.textContent = 'Pan Mode';
            paper.setInteractivity(true);
        }
    });

    // Register the selection instance with the pan button
    registerSelectionWithPanMode(selection, panButton);

    // Zoom controls
    document.getElementById('zoom-in').addEventListener('click', function() {
        var currentScale = paper.scale().sx;
        paper.scale(currentScale * 1.2);
    });

    document.getElementById('zoom-out').addEventListener('click', function() {
        var currentScale = paper.scale().sx;
        paper.scale(currentScale * 0.8);
    });

    document.getElementById('zoom-to-fit').addEventListener('click', function() {
        paper.scaleContentToFit({ padding: 50 });
    });

    // Initialize panning
    paper.on('blank:pointerdown', function(evt, x, y) {
        if (isPanning) {
            var scale = paper.scale();
            var originalPoint = { x: x * scale.sx, y: y * scale.sy };

            document.onmousemove = function(e) {
                var dx = (e.clientX - originalPoint.x) / scale.sx;
                var dy = (e.clientY - originalPoint.y) / scale.sy;
                paper.translate(paper.translate().tx + dx, paper.translate().ty + dy);
            };

            document.onmouseup = function() {
                document.onmousemove = null;
                document.onmouseup = null;
            };
        }
    });

    // Save and load functionality
    document.getElementById('save-graph').addEventListener('click', function() {
        var jsonString = JSON.stringify(graph.toJSON());
        localStorage.setItem('workflow', jsonString);
        alert('Workflow diagram saved!');
    });

    document.getElementById('load-graph').addEventListener('click', function() {
        var savedGraph = localStorage.getItem('workflow');
        if (savedGraph) {
            graph.fromJSON(JSON.parse(savedGraph));
            alert('Workflow diagram loaded!');
        } else {
            alert('No saved workflow found!');
        }
    });

    document.getElementById('clear-graph').addEventListener('click', function() {
        if (confirm('Are you sure you want to clear the diagram?')) {
            graph.clear();
            selection.clear(); // Clear selection as well
        }
    });

    // Initialize custom shapes
    initializeCustomShapes();

    // Make items draggable from palette
    setupDraggablePalette(graph, paper);

    // Setup properties panel
    setupPropertiesPanel(graph, paper);

    // Setup connection points for easier linking
    setupConnectionPoints(paper);

    // Add validation for workflow
    setupValidation(graph);

    // Enable export functionality
    setupExport(graph);

    // Make paper responsive
    const resizeHandler = function() {
        // No need to adjust width as it's 100%
        const height = document.querySelector('.main-content').offsetHeight - document.querySelector('.toolbar').offsetHeight;
        paper.setDimensions('100%', height);
    };

    window.addEventListener('resize', resizeHandler);

    // Initialize paper size
    resizeHandler();

    // Add event handler for cleanup on page unload
    window.addEventListener('beforeunload', function() {
        // Clean up selection to prevent memory leaks
        if (selection && selection.destroy) {
            selection.destroy();
        }

        // Remove event listeners
        window.removeEventListener('resize', resizeHandler);
    });
});
