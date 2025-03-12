// main.js - Updated with palette setup call

document.addEventListener('DOMContentLoaded', function() {
    try {
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
            // Initial interactive settings - will be enhanced by setupConnectionPoints
            interactive: {
                linkMove: true,
                elementMove: true,
                arrowheadMove: true,
                addLinkFromMagnet: true,
                linkPinning: false
            }
        });

        // Define SVG filters for shadow effects
        setupShadowFilters(paper);

        // Enhance the paper's interactive settings for better snapping behavior
        paper.options.snapLinks = {
            radius: 20  // The distance within which a link end will snap to a magnet
        };

        // Create Selection instance
        var selection = new Selection(graph, paper);

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
                    paper.options.interactive = {
                        elementMove: false,
                        linkMove: true,
                        arrowheadMove: true,
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
                    paper.options.interactive = {
                        elementMove: true,
                        linkMove: true,
                        arrowheadMove: true,
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

        // Initialize custom shapes
        if (typeof initializeCustomShapes === 'function') {
            initializeCustomShapes();
        } else {
            console.warn('initializeCustomShapes function not available');
        }

        // Make items draggable from palette - ADD THIS LINE
        if (typeof setupDraggablePalette === 'function') {
            setupDraggablePalette(graph, paper);
        } else {
            console.warn('setupDraggablePalette function not available');
        }

        // Setup connection points for easier linking
        if (typeof setupConnectionPoints === 'function') {
            setupConnectionPoints(paper, graph);
        } else {
            console.warn('setupConnectionPoints function not available');
        }

        // Setup properties panel
        if (typeof setupPropertiesPanel === 'function') {
            setupPropertiesPanel(graph, paper);
        } else {
            console.warn('setupPropertiesPanel function not available');
        }

        // Add validation for workflow
        if (typeof setupValidation === 'function') {
            setupValidation(graph);
        } else {
            console.warn('setupValidation function not available');
        }

        // Enable export functionality
        if (typeof setupExport === 'function') {
            setupExport(graph);
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
                        paper.setDimensions('100%', height);
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
