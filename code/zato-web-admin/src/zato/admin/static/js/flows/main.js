// main.js - Modified to make paper and graph accessible globally

document.addEventListener('DOMContentLoaded', function() {
    try {
        console.log("Initializing workflow editor with reconnection support...");

        // Initialize workflow editor with global variables
        window.graph = new joint.dia.Graph();

        // Create a default link with arrowheadMove enabled
        const defaultLink = new joint.shapes.standard.Link({
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
            connector: { name: 'rounded' },
            // CRITICAL: This enables arrowhead movement for new links
            interactive: {
                arrowheadMove: true
            }
        });

        console.log("Default link created with arrowheadMove:", defaultLink.get('interactive'));

        window.paper = new joint.dia.Paper({
            el: document.getElementById('paper'),
            model: window.graph,
            width: '100%',
            height: '100%',
            gridSize: 10,
            drawGrid: true,
            background: {
                color: 'rgba(0, 0, 0, 0.05)'
            },
            defaultLink: defaultLink,
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
            // CRITICAL: These settings enable reconnection
            interactive: {
                linkPinning: false,        // Don't allow links to be pinned in empty space
                arrowheadMove: true,       // CRITICAL: Allow arrowheads to be moved to connect to elements
                elementMove: true,         // Allow elements to be moved
                addLinkFromMagnet: true,   // Allow links to be created from magnets
                vertexAdd: false,          // Don't allow vertices to be added to links
                vertexRemove: false        // Don't allow vertices to be removed from links
            },
            // CRITICAL: Enable snap behavior
            snapLinks: {
                radius: 20
            }
        });

        console.log("Paper created with arrowheadMove:", window.paper.options.interactive);

        // Add styles to make arrowheads much more clickable
        const arrowheadStyles = document.createElement('style');
        arrowheadStyles.textContent = `
            /* Make arrowheads much larger and more clickable */
            .joint-link .marker-arrowhead {
                cursor: move !important;
                transform-origin: center !important;
                transform: scale(2.5) !important;
            }

            /* Change color on hover for better feedback */
            .joint-link .marker-arrowhead:hover {
                fill: #FF5722 !important;
            }

            /* Make links thicker for easier selection */
            .joint-link .connection, .joint-link .connection-wrap {
                stroke-width: 3px !important;
            }

            /* Make the connection-wrap (the invisible clickable area around links) larger */
            .joint-link .connection-wrap {
                stroke-width: 20px !important;
                opacity: 0 !important;
                cursor: move !important;
            }

            /* Hide port labels */
            .joint-port text {
                display: none;
            }
        `;
        document.head.appendChild(arrowheadStyles);

        // Define SVG filters for shadow effects
        setupShadowFilters(window.paper);

        // Create Selection instance
        var selection = new Selection(window.graph, window.paper);

        // Pan mode
        var isPanning = false;
        var panButton = document.getElementById('pan-paper');

        if (!panButton) {
            console.error('Pan button element not found');
        } else {
            panButton.addEventListener('click', function() {
                isPanning = !isPanning;
                if (isPanning) {
                    this.textContent = 'Selection Mode';

                    // Update selection mode
                    if (selection && typeof selection.setPanningMode === 'function') {
                        selection.setPanningMode(true);
                    }

                    // IMPORTANT: Don't completely disable interactivity
                    // Just selectively disable element movement while keeping link functionality
                    window.paper.options.interactive = {
                        elementMove: false,
                        linkMove: true,
                        arrowheadMove: true,  // KEEP THIS ENABLED
                        addLinkFromMagnet: true,
                        linkPinning: false
                    };
                } else {
                    this.textContent = 'Pan Mode';

                    // Update selection mode
                    if (selection && typeof selection.setPanningMode === 'function') {
                        selection.setPanningMode(false);
                    }

                    // Restore full interactivity
                    window.paper.options.interactive = {
                        elementMove: true,
                        linkMove: true,
                        arrowheadMove: true,  // KEEP THIS ENABLED
                        addLinkFromMagnet: true,
                        linkPinning: false
                    };
                }
            });

            // Register the selection instance with the pan button
            if (typeof registerSelectionWithPanMode === 'function') {
                registerSelectionWithPanMode(selection, panButton);
            } else {
                console.warn('registerSelectionWithPanMode function not available');
            }
        }

        // Initialize panning
        window.paper.on('blank:pointerdown', function(evt, x, y) {
            if (isPanning) {
                var scale = window.paper.scale();
                var originalPoint = { x: x * scale.sx, y: y * scale.sy };

                document.onmousemove = function(e) {
                    var dx = (e.clientX - originalPoint.x) / scale.sx;
                    var dy = (e.clientY - originalPoint.y) / scale.sy;
                    window.paper.translate(window.paper.translate().tx + dx, window.paper.translate().ty + dy);
                };

                document.onmouseup = function() {
                    document.onmousemove = null;
                    document.onmouseup = null;
                };
            }
        });

        // Save and load functionality
        var saveButton = document.getElementById('save-graph');
        var loadButton = document.getElementById('load-graph');
        var clearButton = document.getElementById('clear-graph');

        if (saveButton) {
            saveButton.addEventListener('click', function() {
                try {
                    var jsonString = JSON.stringify(window.graph.toJSON());
                    localStorage.setItem('workflow', jsonString);
                    alert('Workflow diagram saved!');
                } catch (error) {
                    console.error('Error saving workflow:', error);
                    alert('Failed to save workflow: ' + error.message);
                }
            });
        }

        if (loadButton) {
            loadButton.addEventListener('click', function() {
                try {
                    var savedGraph = localStorage.getItem('workflow');
                    if (savedGraph) {
                        var parsedGraph = JSON.parse(savedGraph);
                        window.graph.fromJSON(parsedGraph);

                        // CRITICAL: Make sure loaded links have arrowheadMove enabled
                        window.graph.getLinks().forEach(link => {
                            link.set('interactive', { arrowheadMove: true });
                        });

                        alert('Workflow diagram loaded!');
                    } else {
                        alert('No saved workflow found!');
                    }
                } catch (error) {
                    console.error('Error loading workflow:', error);
                    alert('Failed to load workflow: ' + error.message);
                }
            });
        }

        if (clearButton) {
            clearButton.addEventListener('click', function() {
                if (confirm('Are you sure you want to clear the diagram?')) {
                    window.graph.clear();
                    if (selection && typeof selection.clear === 'function') {
                        selection.clear(); // Clear selection as well
                    }
                }
            });
        }

        // Initialize custom shapes
        if (typeof initializeCustomShapes === 'function') {
            initializeCustomShapes();
        } else {
            console.warn('initializeCustomShapes function not available');
        }

        // Make items draggable from palette
        if (typeof setupDraggablePalette === 'function') {
            setupDraggablePalette(window.graph, window.paper);
        } else {
            console.warn('setupDraggablePalette function not available');
        }

        // Setup properties panel
        if (typeof setupPropertiesPanel === 'function') {
            setupPropertiesPanel(window.graph, window.paper);
        } else {
            console.warn('setupPropertiesPanel function not available');
        }

        // Setup connection points - CRITICAL
        if (typeof setupConnectionPoints === 'function') {
            // Pass along critical settings that need to be applied
            setupConnectionPoints(window.paper, window.graph);

            // CRITICAL: Check and log if arrowheadMove is still enabled
            console.log("After setupConnectionPoints, paper interactive settings:", window.paper.options.interactive);
        } else {
            console.warn('setupConnectionPoints function not available');
        }

        // CRITICAL: Ensure all links have the arrowheadMove setting
        window.graph.on('add', function(cell) {
            if (cell.isLink && cell.isLink()) {
                console.log("Setting arrowheadMove for new link");
                cell.set('interactive', { arrowheadMove: true });
            }
        });

        // Add validation for workflow
        if (typeof setupValidation === 'function') {
            setupValidation(window.graph);
        } else {
            console.warn('setupValidation function not available');
        }

        // Enable export functionality
        if (typeof setupExport === 'function') {
            setupExport(window.graph);
        } else {
            console.warn('setupExport function not available');
        }

        // Make paper responsive
        const resizeHandler = function() {
            try {
                // Get the main content and toolbar elements
                const mainContent = document.querySelector('.main-content');
                const toolbar = document.querySelector('.toolbar');

                if (mainContent && toolbar) {
                    // Calculate the available height
                    const height = mainContent.offsetHeight - toolbar.offsetHeight;

                    // Only update if the height is positive to avoid layout issues
                    if (height > 0) {
                        window.paper.setDimensions('100%', height);
                    }
                }
            } catch (error) {
                console.error('Error in resize handler:', error);
            }
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

        // Add a dummy debug link
        window.debugLink = function() {
            // Create two nodes
            var source = new joint.shapes.workflow.Service();
            source.position(100, 100);
            source.resize(100, 50);
            source.attr('label/text', 'Source');

            var target = new joint.shapes.workflow.Service();
            target.position(300, 100);
            target.resize(100, 50);
            target.attr('label/text', 'Target');

            // Add both to the graph
            window.graph.addCells([source, target]);

            // Create a link with arrowheadMove enabled
            var link = new joint.shapes.standard.Link({
                source: { id: source.id, port: 'out1' },
                target: { id: target.id, port: 'in1' },
                attrs: {
                    line: {
                        stroke: '#FF0000',
                        strokeWidth: 2,
                        targetMarker: {
                            type: 'path',
                            d: 'M 10 -5 0 0 10 5 z'
                        }
                    }
                },
                interactive: { arrowheadMove: true }
            });

            // Add the link to the graph
            window.graph.addCell(link);

            console.log("Debug link created with arrowheadMove:", link.get('interactive'));
            console.log("Try reconnecting the red link");

            return link;
        };

        // Add debug function for testing in console
        window.testReconnect = function() {
            console.log("Paper settings:", window.paper.options.interactive);
            console.log("Registered link events:", Object.keys(window.paper._events).filter(e => e.includes('link')));

            // Monitor link events
            window.paper.on('link:pointerdown', function(linkView, evt) {
                console.log("Link clicked:", linkView.model.id);
                console.log("Event target:", evt.target);
                console.log("Is arrowhead:", evt.target.classList.contains('marker-arrowhead'));
            });

            // Make arrowheads very visible
            window.graph.getLinks().forEach(link => {
                link.attr({
                    '.marker-target': {
                        fill: '#FF0000',
                        stroke: '#FF0000',
                        d: 'M 10 -10 L 20 0 L 10 10 z'  // Make a bigger arrowhead
                    }
                });
            });

            console.log("Debug mode active. Try clicking on arrowheads now.");
        };

        console.log("Initialization complete. For debugging, run window.debugLink() and window.testReconnect() in console");

    } catch (error) {
        console.error('Error initializing workflow editor:', error);
        alert('Failed to initialize workflow editor: ' + error.message);
    }
});

// Define SVG filters for shadow effects
function setupShadowFilters(paper) {
    // Add CSS styles for shadows using more specific selectors
    const style = document.createElement('style');
    style.textContent = `
        .joint-element .joint-cell {
            filter: drop-shadow(2px 3px 4px rgba(0, 0, 0, 0.35));
        }
    `;
    document.head.appendChild(style);

    console.log("CSS-based shadows applied");
    return true;
}
