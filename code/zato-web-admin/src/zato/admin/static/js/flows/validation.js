// validation.js - Workflow validation rules

function setupValidation(graph) {
    const validateButton = document.getElementById('validate-button');
    if (!validateButton) {
        console.error('Validation button element not found');
        return;
    }

    // Keep track of the current open modal
    let currentModal = null;

    validateButton.addEventListener('click', function() {
        // Close any existing modal first
        if (currentModal && currentModal.parentNode) {
            currentModal.parentNode.removeChild(currentModal);
        }

        var validationResults = validateWorkflow(graph);
        displayValidationResults(validationResults);
    });

    function validateWorkflow(graph) {
        var cells = graph.getCells();
        var validationResults = {
            valid: true,
            errors: [],
            warnings: []
        };

        // Check for isolated elements (no connections)
        cells.forEach(function(cell) {
            if (cell.isElement()) {
                var connected = false;
                cells.forEach(function(otherCell) {
                    if (otherCell.isLink()) {
                        if (otherCell.getSourceElement() === cell || otherCell.getTargetElement() === cell) {
                            connected = true;
                        }
                    }
                });

                if (!connected) {
                    validationResults.warnings.push({
                        type: 'Isolated Element',
                        id: cell.id,
                        message: 'Element "' + (cell.attr('label/text') || cell.id) + '" is not connected to any other element.'
                    });
                }
            }
        });

        // Check for dangling links (links that don't connect to elements)
        cells.forEach(function(cell) {
            if (cell.isLink()) {
                var source = cell.getSourceElement();
                var target = cell.getTargetElement();

                if (!source || !target) {
                    validationResults.errors.push({
                        type: 'Dangling Link',
                        id: cell.id,
                        message: 'Link "' + cell.id + '" is not properly connected to elements.'
                    });
                    validationResults.valid = false;
                }
            }
        });

        // Check for start and end nodes
        var hasStart = false;
        var hasEnd = false;

        cells.forEach(function(cell) {
            if (cell.get('type') === 'workflow.Start') {
                hasStart = true;
            }
            if (cell.get('type') === 'workflow.End') {
                hasEnd = true;
            }
        });

        if (!hasStart) {
            validationResults.errors.push({
                type: 'Missing Start',
                message: 'Workflow is missing a Start node.'
            });
            validationResults.valid = false;
        }

        if (!hasEnd) {
            validationResults.errors.push({
                type: 'Missing End',
                message: 'Workflow is missing an End node.'
            });
            validationResults.valid = false;
        }

        // Check for unreachable elements
        if (hasStart) {
            var reachable = {};
            var startNodes = cells.filter(function(cell) {
                return cell.get('type') === 'workflow.Start';
            });

            function markReachable(element) {
                if (!element || reachable[element.id]) return;
                reachable[element.id] = true;

                var outgoingLinks = graph.getConnectedLinks(element, { outbound: true });
                outgoingLinks.forEach(function(link) {
                    var target = link.getTargetElement();
                    if (target) {
                        markReachable(target);
                    }
                });
            }

            startNodes.forEach(markReachable);

            cells.forEach(function(cell) {
                if (cell.isElement() && cell.get('type') !== 'workflow.Start' && !reachable[cell.id]) {
                    validationResults.warnings.push({
                        type: 'Unreachable Element',
                        id: cell.id,
                        message: 'Element "' + (cell.attr('label/text') || cell.id) + '" is not reachable from any Start node.'
                    });
                }
            });
        }

        // Check for cycles using a depth-first search approach
        var hasCycle = detectCycles(graph, cells);

        if (hasCycle) {
            validationResults.warnings.push({
                type: 'Cycle Detected',
                message: 'The workflow contains cycles (loops). Make sure this is intentional.'
            });
        }

        return validationResults;
    }

    // Efficient cycle detection that only processes each node once
    function detectCycles(graph, cells) {
        var visited = {};
        var recStack = {};
        var hasCycle = false;

        // Filter only elements (nodes)
        var elements = cells.filter(function(cell) {
            return cell.isElement();
        });

        function checkCycle(element) {
            if (!element) return false;

            const elementId = element.id;

            // If already processed completely and no cycle found, skip
            if (visited[elementId] && !recStack[elementId]) return false;

            // If not visited, mark as visited
            if (!visited[elementId]) {
                visited[elementId] = true;
                recStack[elementId] = true;

                // Get all outgoing links
                var outgoingLinks = graph.getConnectedLinks(element, { outbound: true });

                // Check each outgoing link
                for (var i = 0; i < outgoingLinks.length; i++) {
                    var target = outgoingLinks[i].getTargetElement();

                    // Skip if target is null (dangling link)
                    if (!target) continue;

                    // If target is in recursion stack, cycle detected
                    if (recStack[target.id]) return true;

                    // Recursive check for cycles from target
                    if (checkCycle(target)) return true;
                }
            }

            // Remove from recursion stack as we're done with this node
            recStack[elementId] = false;
            return false;
        }

        // Try from each unvisited element as a starting point
        // This is more efficient as we skip already processed nodes
        for (var i = 0; i < elements.length; i++) {
            if (!visited[elements[i].id]) {
                if (checkCycle(elements[i])) {
                    hasCycle = true;
                    break;
                }
            }
        }

        return hasCycle;
    }

    function displayValidationResults(results) {
        var message = '';

        if (results.valid && results.warnings.length === 0) {
            message = 'Validation successful: No issues found.';
        } else {
            if (!results.valid) {
                message += '<strong>Validation Failed</strong><br><br>';
                message += '<span style="color: #E74C3C; font-weight: bold;">Errors:</span><br>';
                results.errors.forEach(function(error) {
                    message += '• ' + error.type + ': ' + error.message + '<br>';
                });
                message += '<br>';
            }

            if (results.warnings.length > 0) {
                message += '<span style="color: #F39C12; font-weight: bold;">Warnings:</span><br>';
                results.warnings.forEach(function(warning) {
                    message += '• ' + warning.type + ': ' + warning.message + '<br>';
                });
            }
        }

        // Show the validation results in a custom modal with improved accessibility
        var modal = document.createElement('div');
        currentModal = modal; // Store reference to current modal

        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-labelledby', 'validation-title');
        modal.setAttribute('aria-describedby', 'validation-content');
        modal.style.position = 'fixed';
        modal.style.left = '0';
        modal.style.top = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.backgroundColor = 'rgba(0,0,0,0.4)';
        modal.style.zIndex = '1000';
        modal.style.display = 'flex';
        modal.style.justifyContent = 'center';
        modal.style.alignItems = 'center';

        // Add click event to close modal when clicking outside
        modal.addEventListener('click', function(event) {
            // Only close if the click is directly on the modal background (not its children)
            if (event.target === modal) {
                closeModal();
            }
        });

        var modalContent = document.createElement('div');
        modalContent.style.backgroundColor = '#fefefe';
        modalContent.style.margin = 'auto';
        modalContent.style.padding = '20px';
        modalContent.style.border = '1px solid #888';
        modalContent.style.width = '50%';
        modalContent.style.maxHeight = '70%';
        modalContent.style.overflow = 'auto';
        modalContent.style.borderRadius = '5px';

        var closeButton = document.createElement('button');
        closeButton.innerHTML = '&times;';
        closeButton.style.color = '#aaa';
        closeButton.style.float = 'right';
        closeButton.style.fontSize = '28px';
        closeButton.style.fontWeight = 'bold';
        closeButton.style.cursor = 'pointer';
        closeButton.style.background = 'none';
        closeButton.style.border = 'none';
        closeButton.setAttribute('aria-label', 'Close validation results');

        // Function to clean up modal and event listeners
        function closeModal() {
            if (modal.parentNode) {
                document.body.removeChild(modal);
            }
            document.removeEventListener('keydown', handleEscKey);
            currentModal = null;
        }

        closeButton.onclick = closeModal;

        var title = document.createElement('h3');
        title.textContent = 'Workflow Validation Results';
        title.style.marginTop = '0';
        title.id = 'validation-title';

        var content = document.createElement('div');
        content.innerHTML = message;
        content.id = 'validation-content';

        modalContent.appendChild(closeButton);
        modalContent.appendChild(title);
        modalContent.appendChild(content);
        modal.appendChild(modalContent);

        document.body.appendChild(modal);

        // Focus the close button for keyboard accessibility
        closeButton.focus();

        // Add keyboard event listener for ESC key
        function handleEscKey(event) {
            if (event.key === 'Escape') {
                closeModal();
            }
        }

        document.addEventListener('keydown', handleEscKey);
    }
}
