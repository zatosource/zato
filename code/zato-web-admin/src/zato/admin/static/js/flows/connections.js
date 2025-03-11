// connections.js - Connection points and linking functionality

function setupConnectionPoints(paper) {
    if (!paper) {
        console.error("Paper object is not provided to setupConnectionPoints");
        return;
    }

    // Enable link creation from elements with ports
    paper.on('element:pointerdown', function(elementView, evt) {
        paper.options.interactive = {
            linkPinning: false,
            addLinkFromMagnet: true
        };
    });

    // Create connecting ports when element is added
    if (paper.model) {
        paper.model.on('add', function(cell) {
            if (cell && typeof cell.isElement === 'function' && cell.isElement()) {
                // Add ports for connections
                if (typeof cell.hasPorts !== 'function' || !cell.hasPorts()) {
                    addDefaultPorts(cell);
                }
            }
        });
    }

    // Add default ports to the element
    function addDefaultPorts(element) {
        // Skip if the element already has ports
        if (element.prop('ports/items')) return;

        // Define port groups
        element.prop('ports/groups/in', {
            position: function(ports, elBBox) {
                // Position inputs evenly along the left side
                return ports.map(function(port, index, ports) {
                    var step = elBBox.height / (ports.length + 1);
                    return {
                        x: 0,
                        y: step * (index + 1)
                    };
                });
            },
            attrs: {
                circle: {
                    r: 6,
                    magnet: 'passive',  // Can receive connections
                    stroke: '#31d0c6',
                    strokeWidth: 2,
                    fill: '#fff'
                },
                text: {
                    fontSize: 10,
                    fill: '#333'
                }
            },
            label: {
                position: {
                    name: 'left',
                    args: {
                        y: 0
                    }
                }
            }
        });

        element.prop('ports/groups/out', {
            position: function(ports, elBBox) {
                // Position outputs evenly along the right side
                return ports.map(function(port, index, ports) {
                    var step = elBBox.height / (ports.length + 1);
                    return {
                        x: elBBox.width,
                        y: step * (index + 1)
                    };
                });
            },
            attrs: {
                circle: {
                    r: 6,
                    magnet: true,  // Can initiate connections
                    stroke: '#31d0c6',
                    strokeWidth: 2,
                    fill: '#fff'
                },
                text: {
                    fontSize: 10,
                    fill: '#333'
                }
            },
            label: {
                position: {
                    name: 'right',
                    args: {
                        y: 0
                    }
                }
            }
        });

        // Get element type
        var elementType = element.get('type');

        // Add the ports based on element type
        if (elementType === 'workflow.Start') {
            // Start only has outputs
            element.addPorts([
                { group: 'out', id: 'out1', attrs: { text: { text: 'Out' } } }
            ]);
        } else if (elementType === 'workflow.Stop') {
            // Stop only has inputs
            element.addPorts([
                { group: 'in', id: 'in1', attrs: { text: { text: 'In' } } }
            ]);
        } else if (elementType === 'workflow.Service') {
            // Service has one input and one output
            element.addPorts([
                { group: 'in', id: 'in1', attrs: { text: { text: 'In' } } },
                { group: 'out', id: 'out1', attrs: { text: { text: 'Out' } } }
            ]);
        } else if (elementType === 'workflow.Parallel') {
            // Parallel has one input and multiple outputs
            element.addPorts([
                { group: 'in', id: 'in1', attrs: { text: { text: 'In' } } },
                { group: 'out', id: 'out1', attrs: { text: { text: 'Out 1' } } },
                { group: 'out', id: 'out2', attrs: { text: { text: 'Out 2' } } },
                { group: 'out', id: 'out3', attrs: { text: { text: 'Out 3' } } }
            ]);
        } else if (elementType === 'workflow.ForkJoin') {
            // ForkJoin has multiple inputs and one output
            element.addPorts([
                { group: 'in', id: 'in1', attrs: { text: { text: 'In 1' } } },
                { group: 'in', id: 'in2', attrs: { text: { text: 'In 2' } } },
                { group: 'in', id: 'in3', attrs: { text: { text: 'In 3' } } },
                { group: 'out', id: 'out1', attrs: { text: { text: 'Out' } } }
            ]);
        } else {
            // Default ports for other or legacy element types
            element.addPorts([
                { group: 'in', id: 'in1', attrs: { text: { text: 'In' } } },
                { group: 'out', id: 'out1', attrs: { text: { text: 'Out' } } }
            ]);
        }
    }
}
