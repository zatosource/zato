// validation.js - Workflow validation rules

function setupValidation(graph) {
    document.getElementById('validate-button').addEventListener('click', function() {
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
                if (reachable[element.id]) return;
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

        // Check for cycles (basic check)
        var visited = {};
        var recStack = {};
        var hasCycle = false;

        function checkCycle(element) {
            if (!visited[element.id]) {
                visited[element.id] = true;
                recStack[element.id] = true;

                var outgoingLinks = graph.getConnectedLinks(element, { outbound: true });
                for (var i = 0; i < outgoingLinks.length; i++) {
                    var target = outgoingLinks[i].getTargetElement();
                    if (target) {
                        if (!visited[target.id] && checkCycle(target)) {
                            return true;
                        } else if (recStack[target.id]) {
                            return true;
                        }
                    }
                }
            }

            recStack[element.id] = false;
            return false;
        }

        cells.forEach(function(cell) {
            if (cell.isElement() && !visited[cell.id]) {
                if (checkCycle(cell)) {
                    hasCycle = true;
                }
            }
        });

        if (hasCycle) {
            validationResults.warnings.push({
                type: 'Cycle Detected',
                message: 'The workflow contains cycles (loops). Make sure this is intentional.'
            });
        }

        return validationResults;
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

        // Show the validation results in a custom modal
        var modal = document.createElement('div');
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

        var modalContent = document.createElement('div');
        modalContent.style.backgroundColor = '#fefefe';
        modalContent.style.margin = 'auto';
        modalContent.style.padding = '20px';
        modalContent.style.border = '1px solid #888';
        modalContent.style.width = '50%';
        modalContent.style.maxHeight = '70%';
        modalContent.style.overflow = 'auto';
        modalContent.style.borderRadius = '5px';

        var closeButton = document.createElement('span');
        closeButton.innerHTML = '&times;';
        closeButton.style.color = '#aaa';
        closeButton.style.float = 'right';
        closeButton.style.fontSize = '28px';
        closeButton.style.fontWeight = 'bold';
        closeButton.style.cursor = 'pointer';

        closeButton.onclick = function() {
            document.body.removeChild(modal);
        };

        var title = document.createElement('h3');
        title.textContent = 'Workflow Validation Results';
        title.style.marginTop = '0';

        var content = document.createElement('div');
        content.innerHTML = message;

        modalContent.appendChild(closeButton);
        modalContent.appendChild(title);
        modalContent.appendChild(content);
        modal.appendChild(modalContent);

        document.body.appendChild(modal);
    }
}
