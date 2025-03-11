// connections.js - Connection points and linking functionality with improved validation

function setupConnectionPoints(paper) {
    if (!paper) {
        console.error("Paper object is not provided to setupConnectionPoints");
        return;
    }

    // Set default paper interactive settings for linking
    paper.options.interactive = {
        linkPinning: false,        // Don't allow links to be pinned in empty space
        vertexAdd: false,          // Don't allow vertices to be added to links
        vertexRemove: false,       // Don't allow vertices to be removed from links
        arrowheadMove: true,       // Allow arrowheads to be moved to connect to elements
        elementMove: true,         // Allow elements to be moved
        addLinkFromMagnet: true    // CRITICAL: Allow links to be created from magnets
    };

    // Enable proper snap behavior for links
    paper.options.snapLinks = {
        radius: 20  // The distance within which links will snap to magnets
    };

    // Set up connection validation
    paper.options.validateConnection = function(sourceView, sourceMagnet, targetView, targetMagnet) {
        try {
            // Don't allow connections to the same element
            if (sourceView.model.id === targetView.model.id) {
                console.log("Connection rejected: Cannot connect to the same element");
                return false;
            }

            // Only allow connections to magnets
            if (!targetMagnet || !sourceMagnet) {
                console.log("Connection rejected: Both source and target must have magnets");
                return false;
            }

            // Get port groups to determine if they're inputs or outputs
            // First try the port-group attribute
            let sourcePortGroup = sourceMagnet.getAttribute('port-group');
            let targetPortGroup = targetMagnet.getAttribute('port-group');

            // If port-group attribute doesn't exist, try to infer from the DOM structure
            if (!sourcePortGroup) {
                const sourcePortEl = sourceMagnet.closest('.joint-port');
                if (sourcePortEl) {
                    const portId = sourcePortEl.getAttribute('port');
                    if (portId) {
                        const port = sourceView.model.getPort(portId);
                        if (port) {
                            sourcePortGroup = port.group;
                        }
                    }
                }
            }

            if (!targetPortGroup) {
                const targetPortEl = targetMagnet.closest('.joint-port');
                if (targetPortEl) {
                    const portId = targetPortEl.getAttribute('port');
                    if (portId) {
                        const port = targetView.model.getPort(portId);
                        if (port) {
                            targetPortGroup = port.group;
                        }
                    }
                }
            }

            // If we still don't have port groups, fall back to checking magnet position
            // (right side = out, left side = in)
            if (!sourcePortGroup) {
                const elementBBox = sourceView.model.getBBox();
                const magnetPosition = sourceView.getConnectionPoint(sourceMagnet, elementBBox);
                sourcePortGroup = (magnetPosition.x > elementBBox.x + elementBBox.width/2) ? 'out' : 'in';
            }

            if (!targetPortGroup) {
                const elementBBox = targetView.model.getBBox();
                const magnetPosition = targetView.getConnectionPoint(targetMagnet, elementBBox);
                targetPortGroup = (magnetPosition.x < elementBBox.x + elementBBox.width/2) ? 'in' : 'out';
            }

            // Check if this is an output port to input port connection
            if (sourcePortGroup === 'out' && targetPortGroup === 'in') {
                console.log("Connection allowed: out -> in");
                return true;
            }

            // Reject in -> in, out -> out, or in -> out connections
            console.log(`Connection rejected: ${sourcePortGroup} -> ${targetPortGroup}`);
            return false;
        } catch (error) {
            console.error("Error in validateConnection:", error);
            return false; // Reject connection on error
        }
    };

    // Validate link reconnections too
    paper.options.validateMagnet = function(cellView, magnet) {
        try {
            // Only allow starting connections from output ports
            // First try the port-group attribute
            let portGroup = magnet.getAttribute('port-group');

            // If the attribute doesn't exist, try to infer from element structure
            if (!portGroup) {
                const portEl = magnet.closest('.joint-port');
                if (portEl) {
                    const portId = portEl.getAttribute('port');
                    if (portId) {
                        const port = cellView.model.getPort(portId);
                        if (port) {
                            portGroup = port.group;
                        }
                    }
                }
            }

            // If we still don't have port group, fall back to position
            if (!portGroup) {
                const elementBBox = cellView.model.getBBox();
                const magnetPosition = cellView.getConnectionPoint(magnet, elementBBox);

                // Right side = out, left side = in
                portGroup = (magnetPosition.x > elementBBox.x + elementBBox.width/2) ? 'out' : 'in';
            }

            if (portGroup === 'out') {
                console.log("Starting connection from output port allowed");
                return true;
            }

            console.log("Cannot start connection from input port");
            return false;
        } catch (error) {
            console.error("Error in validateMagnet:", error);
            return false; // Reject on error
        }
    };

    // Create connecting ports when element is added
    if (paper.model) {
        paper.model.on('add', function(cell) {
            if (cell && typeof cell.isElement === 'function' && cell.isElement()) {
                // Add ports for connections if they don't exist
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
                    fill: '#fff',
                    'port-group': 'in'  // Mark as input port for validation
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
                    magnet: true,       // CRITICAL: Must be 'true' to allow initiating connections
                    stroke: '#31d0c6',
                    strokeWidth: 2,
                    fill: '#fff',
                    'port-group': 'out'  // Mark as output port for validation
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

    // Provide better visual feedback for invalid connections
    paper.on('link:connect', function(linkView) {
        updateLinkValidityVisual(linkView);
    });

    // Update when link is changed
    paper.model.on('change:source change:target', function(link) {
        if (link.isLink()) {
            const linkView = link.findView(paper);
            if (linkView) {
                updateLinkValidityVisual(linkView);
            }
        }
    });

    // Update link visual based on connection validity
    function updateLinkValidityVisual(linkView) {
        try {
            const link = linkView.model;

            // Get source and target elements
            const sourceElement = link.getSourceElement();
            const targetElement = link.getTargetElement();

            if (!sourceElement || !targetElement) return;

            // Get source and target port IDs from link attributes
            const sourcePortId = link.get('source').port;
            const targetPortId = link.get('target').port;

            if (!sourcePortId || !targetPortId) return;

            // Get port groups from the elements
            const sourcePort = sourceElement.getPort(sourcePortId);
            const targetPort = targetElement.getPort(targetPortId);

            if (!sourcePort || !targetPort) return;

            const sourcePortGroup = sourcePort.group;
            const targetPortGroup = targetPort.group;

            // Determine if connection is valid (out -> in)
            const isValid = (sourcePortGroup === 'out' && targetPortGroup === 'in');

            // Update link visual based on validity
            if (isValid) {
                link.attr({
                    line: {
                        stroke: '#333333',
                        strokeWidth: 2,
                        'stroke-dasharray': ''
                    }
                });
            } else {
                // Invalid connection - show as dashed red
                link.attr({
                    line: {
                        stroke: '#FF0000',
                        strokeWidth: 2,
                        'stroke-dasharray': '5,5'
                    }
                });
            }
        } catch (error) {
            console.error("Error updating link validity visual:", error);
        }
    }
}
