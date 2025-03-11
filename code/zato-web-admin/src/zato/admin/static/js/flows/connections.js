// connections.js - Connection points and linking functionality with improved validation

function setupConnectionPoints(paper) {
    if (!paper) {
        console.error("Paper object is not provided to setupConnectionPoints");
        return;
    }

    // Track connections that need to be flipped
    let pendingFlip = null;

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
            let sourcePortGroup = sourceMagnet.getAttribute('port-group');
            let targetPortGroup = targetMagnet.getAttribute('port-group');

            // If attributes not found, try to get from the port element
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

            // Case 1: Normal direction - output to input
            if (sourcePortGroup === 'out' && targetPortGroup === 'in') {
                console.log("Connection allowed: out -> in");
                pendingFlip = null; // No need to flip
                return true;
            }

            // Case 2: Reverse direction - input to output (will be flipped)
            if (sourcePortGroup === 'in' && targetPortGroup === 'out') {
                console.log("Connection allowed (will be flipped): in -> out");

                // Mark this connection for flipping
                pendingFlip = {
                    sourceId: sourceView.model.id,
                    sourcePort: sourceMagnet.getAttribute('port'),
                    targetId: targetView.model.id,
                    targetPort: targetMagnet.getAttribute('port')
                };

                return true;
            }

            // Reject all other connection types
            console.log(`Connection rejected: ${sourcePortGroup} -> ${targetPortGroup}`);
            return false;
        } catch (error) {
            console.error("Error in validateConnection:", error);
            return false; // Reject on error
        }
    };

    // Validate magnet to allow starting connections from both input and output ports
    paper.options.validateMagnet = function(cellView, magnet) {
        try {
            // Check port group to determine if it's an input or output port
            let portGroup = magnet.getAttribute('port-group');

            // If attribute not found, try to get from the port element
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

            // Allow connections from both input and output ports
            if (portGroup === 'out' || portGroup === 'in') {
                return true;
            }

            return false;
        } catch (error) {
            console.error("Error in validateMagnet:", error);
            return false; // Reject on error
        }
    };

    // Add handler to flip connections immediately after they're connected
    paper.on('link:connect', function(linkView) {
        if (!pendingFlip) return;

        const link = linkView.model;
        const source = link.get('source');
        const target = link.get('target');

        // Check if this is the link we need to flip
        if (source.id === pendingFlip.sourceId &&
            target.id === pendingFlip.targetId) {

            console.log("Flipping connection direction...");

            try {
                // Create a new link with reversed endpoints
                const newLink = link.clone();
                if (!newLink) {
                    console.error("Failed to clone link for flipping");
                    return;
                }

                // Set the source and target to be flipped
                newLink.set('source', { id: pendingFlip.targetId, port: pendingFlip.targetPort });
                newLink.set('target', { id: pendingFlip.sourceId, port: pendingFlip.sourcePort });

                // Add the new link to the graph
                paper.model.addCell(newLink);

                // Remove the original link
                link.remove();

                console.log("Connection successfully flipped");
            } catch (error) {
                console.error("Error during connection flip:", error);
            } finally {
                // Reset the pending flip data
                pendingFlip = null;
            }
        }
    });

    // Handle dangling links (incomplete connections)
    paper.on('blank:pointerup', function() {
        removeDanglingLinks();
        pendingFlip = null; // Reset on blank click
    });

    paper.on('cell:pointerup', function() {
        setTimeout(removeDanglingLinks, 100);
    });

    function removeDanglingLinks() {
        const links = paper.model.getLinks();
        links.forEach(function(link) {
            const source = link.get('source');
            const target = link.get('target');

            const sourceOk = source && source.id && source.port;
            const targetOk = target && target.id && target.port;

            if (!sourceOk || !targetOk) {
                link.remove();
                console.log("Removed dangling link");
            }
        });
    }

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

        // Add CSS styles for port labels
        const style = document.createElement('style');
        style.textContent = `
            /* Hide port labels by default */
            .joint-port text {
                opacity: 0;
                transition: opacity 0.2s;
            }

            /* Show port labels on hover */
            .joint-port:hover text {
                opacity: 1;
            }
        `;
        document.head.appendChild(style);
    }

    // Add default ports to the element
    function addDefaultPorts(element) {
        // Skip if the element already has ports
        if (element.prop('ports/items')) return;

        // Define port groups with ports on border but labels inside
        element.prop('ports/groups/in', {
            position: function(ports, elBBox) {
                // Position inputs on the left border
                return ports.map(function(port, index, ports) {
                    var step = elBBox.height / (ports.length + 1);
                    return {
                        // Position on the left border (x=0)
                        x: 0,
                        y: step * (index + 1)
                    };
                });
            },
            attrs: {
                circle: {
                    r: 6,
                    magnet: true,  // Allow input ports to initiate connections
                    stroke: '#31d0c6',
                    strokeWidth: 2,
                    fill: '#fff',
                    'port-group': 'in'  // Mark as input port
                },
                text: {
                    fontSize: 10,
                    fill: '#333',
                    textAnchor: 'start',  // Left-align the text
                    textVerticalAnchor: 'middle',  // Center vertically
                    dx: 15  // Position the text 15px from the port (inside)
                }
            }
        });

        element.prop('ports/groups/out', {
            position: function(ports, elBBox) {
                // Position outputs on the right border
                return ports.map(function(port, index, ports) {
                    var step = elBBox.height / (ports.length + 1);
                    return {
                        // Position on the right border (x=width)
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
                    fill: '#fff',
                    'port-group': 'out'  // Mark as output port
                },
                text: {
                    fontSize: 10,
                    fill: '#333',
                    textAnchor: 'end',  // Right-align the text
                    textVerticalAnchor: 'middle',  // Center vertically
                    dx: -15  // Position the text 15px from the port toward inside
                }
            }
        });

        // Get element type
        var elementType = element.get('type');

        // Add the ports based on element type
        if (elementType === 'workflow.Start') {
            // Start only has outputs
            element.addPorts([
                { group: 'out', id: 'out1', attrs: { text: { text: '' } } }
            ]);
        } else if (elementType === 'workflow.Stop') {
            // Stop only has inputs
            element.addPorts([
                { group: 'in', id: 'in1', attrs: { text: { text: '' } } }
            ]);
        } else if (elementType === 'workflow.Service') {
            // Service has one input and one output
            element.addPorts([
                { group: 'in', id: 'in1', attrs: { text: { text: '' } } },
                { group: 'out', id: 'out1', attrs: { text: { text: '' } } }
            ]);
        } else if (elementType === 'workflow.Parallel') {
            // Parallel has one input and multiple outputs
            element.addPorts([
                { group: 'in', id: 'in1', attrs: { text: { text: '' } } },
                { group: 'out', id: 'out1', attrs: { text: { text: '' } } }
            ]);
        } else if (elementType === 'workflow.ForkJoin') {
            // ForkJoin has multiple inputs and one output
            element.addPorts([
                { group: 'in', id: 'in1', attrs: { text: { text: '' } } },
                { group: 'out', id: 'out1', attrs: { text: { text: '' } } }
            ]);
        } else {
            // Default ports for other or legacy element types
            element.addPorts([
                { group: 'in', id: 'in1', attrs: { text: { text: '' } } },
                { group: 'out', id: 'out1', attrs: { text: { text: '' } } }
            ]);
        }
    }
}
