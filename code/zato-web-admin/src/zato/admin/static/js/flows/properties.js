// properties.js - Properties panel for editing elements with shadow controls

function setupPropertiesPanel(graph, paper) {
    var propertiesContent = document.getElementById('properties-content');
    var selectedElement = null;

    if (!propertiesContent) {
        console.error("Properties panel content element not found");
        return;
    }

    paper.on('element:pointerclick', function(elementView) {
        selectedElement = elementView.model;
        updatePropertiesPanel(selectedElement);
    });

    paper.on('link:pointerclick', function(linkView) {
        selectedElement = linkView.model;
        updatePropertiesPanel(selectedElement);
    });

    paper.on('blank:pointerclick', function() {
        selectedElement = null;
        propertiesContent.innerHTML = '<div class="empty-properties">Select an element to view properties</div>';
    });

    function updatePropertiesPanel(element) {
        if (!element) return;

        propertiesContent.innerHTML = '';

        var isLink = element.isLink();
        var elementType = element.get('type') || '';

        // Common properties
        var idLabel = document.createElement('label');
        idLabel.innerText = 'ID:';
        propertiesContent.appendChild(idLabel);

        var idInput = document.createElement('input');
        idInput.type = 'text';
        idInput.value = element.id;
        idInput.readOnly = true;
        propertiesContent.appendChild(idInput);

        // Type label
        var typeLabel = document.createElement('label');
        typeLabel.innerText = 'Type:';
        propertiesContent.appendChild(typeLabel);

        var typeDisplay = document.createElement('input');
        typeDisplay.type = 'text';
        typeDisplay.value = getDisplayNameForType(elementType);
        typeDisplay.readOnly = true;
        propertiesContent.appendChild(typeDisplay);

        // Element-specific properties
        if (!isLink) {
            addElementProperties(element, elementType);
        } else {
            addLinkProperties(element);
        }

        // Delete button for any element
        var deleteButton = document.createElement('button');
        deleteButton.innerText = 'Delete Element';
        deleteButton.style.backgroundColor = '#E74C3C';
        deleteButton.style.color = 'white';
        deleteButton.style.border = 'none';
        deleteButton.style.padding = '8px';
        deleteButton.style.marginTop = '15px';
        deleteButton.style.width = '100%';
        deleteButton.style.cursor = 'pointer';

        deleteButton.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this element?')) {
                element.remove();
                propertiesContent.innerHTML = '<div class="empty-properties">Select an element to view properties</div>';
            }
        });

        propertiesContent.appendChild(deleteButton);
    }

    function getDisplayNameForType(type) {
        // Convert the technical type name to a user-friendly name
        var displayNames = {
            'workflow.Start': 'Start',
            'workflow.Stop': 'Stop',
            'workflow.Service': 'Service',
            'workflow.Parallel': 'Parallel',
            'workflow.ForkJoin': 'Fork/Join'
        };

        return displayNames[type] || type;
    }

    function addElementProperties(element, elementType) {
        // Label
        var labelLabel = document.createElement('label');
        labelLabel.innerText = 'Label:';
        propertiesContent.appendChild(labelLabel);

        var labelInput = document.createElement('input');
        labelInput.type = 'text';
        labelInput.value = element.attr('label/text') || '';
        labelInput.addEventListener('change', function() {
            element.attr('label/text', this.value);
        });
        propertiesContent.appendChild(labelInput);

        // Fill color - handle different element types
        var fillLabel = document.createElement('label');
        fillLabel.innerText = 'Fill Color:';
        propertiesContent.appendChild(fillLabel);

        var fillAttr = 'body/fill';
        // For Path elements like octagonal Start/Stop, the fill attribute might be different
        if (elementType === 'workflow.Start' || elementType === 'workflow.Stop') {
            fillAttr = 'body/fill';
        }

        var fillInput = document.createElement('input');
        fillInput.type = 'color';
        fillInput.value = ensureValidColor(element.attr(fillAttr) || '#FFFFFF');
        fillInput.addEventListener('change', function() {
            element.attr(fillAttr, this.value);
        });
        propertiesContent.appendChild(fillInput);

        // Stroke color - handle different element types
        var strokeLabel = document.createElement('label');
        strokeLabel.innerText = 'Border Color:';
        propertiesContent.appendChild(strokeLabel);

        var strokeAttr = 'body/stroke';
        // For Path elements like octagonal Start/Stop, the stroke attribute might be different
        if (elementType === 'workflow.Start' || elementType === 'workflow.Stop') {
            strokeAttr = 'body/stroke';
        }

        var strokeInput = document.createElement('input');
        strokeInput.type = 'color';
        strokeInput.value = ensureValidColor(element.attr(strokeAttr) || '#000000');
        strokeInput.addEventListener('change', function() {
            element.attr(strokeAttr, this.value);
        });
        propertiesContent.appendChild(strokeInput);

        // Width
        var widthLabel = document.createElement('label');
        widthLabel.innerText = 'Width:';
        propertiesContent.appendChild(widthLabel);

        var size = element.get('size') || { width: 100, height: 100 };
        var widthInput = document.createElement('input');
        widthInput.type = 'number';
        widthInput.min = 20;
        widthInput.max = 500;
        widthInput.value = size.width || 100;
        widthInput.addEventListener('change', function() {
            var currentSize = element.get('size') || { width: 100, height: 100 };
            element.resize(parseInt(this.value), currentSize.height);
        });
        propertiesContent.appendChild(widthInput);

        // Height
        var heightLabel = document.createElement('label');
        heightLabel.innerText = 'Height:';
        propertiesContent.appendChild(heightLabel);

        var heightInput = document.createElement('input');
        heightInput.type = 'number';
        heightInput.min = 20;
        heightInput.max = 500;
        heightInput.value = size.height || 100;
        heightInput.addEventListener('change', function() {
            var currentSize = element.get('size') || { width: 100, height: 100 };
            element.resize(currentSize.width, parseInt(this.value));
        });
        propertiesContent.appendChild(heightInput);

        // Shadow Controls
        addShadowControls(element);

        // Add element-specific properties based on the type
        if (elementType === 'workflow.Service') {
            addServiceProperties(element);
        } else if (elementType === 'workflow.Parallel') {
            addParallelProperties(element);
        } else if (elementType === 'workflow.ForkJoin') {
            addForkJoinProperties(element);
        }

        // Custom data section
        var customDataLabel = document.createElement('label');
        customDataLabel.innerText = 'Custom Data:';
        propertiesContent.appendChild(customDataLabel);

        var customDataContainer = document.createElement('div');
        customDataContainer.className = 'custom-data-container';
        propertiesContent.appendChild(customDataContainer);

        var customDataInput = document.createElement('textarea');
        customDataInput.rows = 5;
        customDataInput.value = JSON.stringify(element.get('customData') || {}, null, 2);
        customDataContainer.appendChild(customDataInput);

        var errorContainer = document.createElement('div');
        errorContainer.className = 'json-error';
        errorContainer.style.display = 'none';
        customDataContainer.appendChild(errorContainer);

        customDataInput.addEventListener('change', function() {
            try {
                var customData = JSON.parse(this.value);
                element.set('customData', customData);
                this.style.borderColor = '';
                errorContainer.style.display = 'none';
            } catch (e) {
                this.style.borderColor = 'red';
                errorContainer.innerHTML = '<div style="color: red; font-size: 12px;">Invalid JSON: ' + e.message + '</div>';
                errorContainer.style.display = 'block';
            }
        });
    }

    // Add shadow controls to the properties panel
    function addShadowControls(element) {
        // Create a section for shadow properties
        var shadowHeader = document.createElement('h4');
        shadowHeader.innerText = 'Shadow';
        shadowHeader.style.marginTop = '15px';
        shadowHeader.style.marginBottom = '5px';
        shadowHeader.style.borderBottom = '1px solid #ddd';
        propertiesContent.appendChild(shadowHeader);

        // Shadow toggle
        var shadowToggleContainer = document.createElement('div');
        shadowToggleContainer.style.display = 'flex';
        shadowToggleContainer.style.alignItems = 'center';
        shadowToggleContainer.style.marginBottom = '10px';
        propertiesContent.appendChild(shadowToggleContainer);

        var shadowToggleLabel = document.createElement('label');
        shadowToggleLabel.innerText = 'Enable Shadow:';
        shadowToggleLabel.style.marginRight = '10px';
        shadowToggleContainer.appendChild(shadowToggleLabel);

        var shadowToggle = document.createElement('input');
        shadowToggle.type = 'checkbox';

        // Check if the element currently has a shadow filter
        var hasFilter = element.attr('body/filter') &&
                       (element.attr('body/filter').name === 'element-shadow' ||
                        element.attr('body/filter') === 'url(#element-shadow)');

        shadowToggle.checked = hasFilter;

        shadowToggle.addEventListener('change', function() {
            if (this.checked) {
                // Apply shadow filter
                element.attr('body/filter', { name: 'element-shadow' });
            } else {
                // Remove shadow filter
                element.attr('body/filter', '');
            }
        });

        shadowToggleContainer.appendChild(shadowToggle);
    }

    function addServiceProperties(element) {
        // Service URL
        var urlLabel = document.createElement('label');
        urlLabel.innerText = 'Service URL:';
        propertiesContent.appendChild(urlLabel);

        var urlInput = document.createElement('input');
        urlInput.type = 'text';
        urlInput.placeholder = 'https://example.com/api';

        // Get customData.serviceUrl if it exists, otherwise empty
        var customData = element.get('customData') || {};
        urlInput.value = customData.serviceUrl || '';

        urlInput.addEventListener('change', function() {
            var customData = element.get('customData') || {};
            customData.serviceUrl = this.value;
            element.set('customData', customData);
        });
        propertiesContent.appendChild(urlInput);
    }

    function addParallelProperties(element) {
        // Number of branches
        var branchesLabel = document.createElement('label');
        branchesLabel.innerText = 'Number of Branches:';
        propertiesContent.appendChild(branchesLabel);

        var branchesInput = document.createElement('input');
        branchesInput.type = 'number';
        branchesInput.min = 2;
        branchesInput.max = 10;

        // Get customData.branches if it exists, otherwise default to 3
        var customData = element.get('customData') || {};
        branchesInput.value = customData.branches || 3;

        branchesInput.addEventListener('change', function() {
            var customData = element.get('customData') || {};
            customData.branches = parseInt(this.value);
            element.set('customData', customData);
        });
        propertiesContent.appendChild(branchesInput);
    }

    function addForkJoinProperties(element) {
        // Join type
        var joinTypeLabel = document.createElement('label');
        joinTypeLabel.innerText = 'Join Type:';
        propertiesContent.appendChild(joinTypeLabel);

        var joinTypeSelect = document.createElement('select');
        var joinTypes = [
            { value: 'all', text: 'Wait for All' },
            { value: 'any', text: 'Wait for Any' },
            { value: 'custom', text: 'Custom Condition' }
        ];

        joinTypes.forEach(function(type) {
            var option = document.createElement('option');
            option.value = type.value;
            option.textContent = type.text;
            joinTypeSelect.appendChild(option);
        });

        // Get customData.joinType if it exists, otherwise default to 'all'
        var customData = element.get('customData') || {};
        joinTypeSelect.value = customData.joinType || 'all';

        joinTypeSelect.addEventListener('change', function() {
            var customData = element.get('customData') || {};
            customData.joinType = this.value;
            element.set('customData', customData);
        });
        propertiesContent.appendChild(joinTypeSelect);
    }

    function addLinkProperties(element) {
        // Link label
        var linkLabelLabel = document.createElement('label');
        linkLabelLabel.innerText = 'Label:';
        propertiesContent.appendChild(linkLabelLabel);

        var linkLabelInput = document.createElement('input');
        linkLabelInput.type = 'text';
        linkLabelInput.value = element.label(0) ? element.label(0).attrs.text.text : '';
        linkLabelInput.addEventListener('change', function() {
            if (this.value) {
                element.label(0, {
                    position: 0.5,
                    attrs: {
                        text: { text: this.value }
                    }
                });
            } else {
                element.removeLabel(0);
            }
        });
        propertiesContent.appendChild(linkLabelInput);

        // Link color
        var linkColorLabel = document.createElement('label');
        linkColorLabel.innerText = 'Line Color:';
        propertiesContent.appendChild(linkColorLabel);

        var linkColorInput = document.createElement('input');
        linkColorInput.type = 'color';
        linkColorInput.value = ensureValidColor(element.attr('line/stroke') || '#000000');
        linkColorInput.addEventListener('change', function() {
            element.attr('line/stroke', this.value);
        });
        propertiesContent.appendChild(linkColorInput);

        // Link thickness
        var linkThicknessLabel = document.createElement('label');
        linkThicknessLabel.innerText = 'Line Thickness:';
        propertiesContent.appendChild(linkThicknessLabel);

        var linkThicknessInput = document.createElement('input');
        linkThicknessInput.type = 'number';
        linkThicknessInput.min = 1;
        linkThicknessInput.max = 10;
        linkThicknessInput.value = element.attr('line/strokeWidth') || 2;
        linkThicknessInput.addEventListener('change', function() {
            element.attr('line/strokeWidth', parseInt(this.value));
        });
        propertiesContent.appendChild(linkThicknessInput);

        // Link style
        var linkStyleLabel = document.createElement('label');
        linkStyleLabel.innerText = 'Line Style:';
        propertiesContent.appendChild(linkStyleLabel);

        var linkStyleSelect = document.createElement('select');
        var styles = [
            { value: '', text: 'Solid' },
            { value: '5,5', text: 'Dashed' },
            { value: '2,2', text: 'Dotted' },
            { value: '10,5,5,5', text: 'Dash Dot' }
        ];

        styles.forEach(function(style) {
            var option = document.createElement('option');
            option.value = style.value;
            option.text = style.text;
            linkStyleSelect.appendChild(option);
        });

        linkStyleSelect.value = element.attr('line/strokeDasharray') || '';
        linkStyleSelect.addEventListener('change', function() {
            element.attr('line/strokeDasharray', this.value);
        });
        propertiesContent.appendChild(linkStyleSelect);

        // Router type
        var routerLabel = document.createElement('label');
        routerLabel.innerText = 'Router Type:';
        propertiesContent.appendChild(routerLabel);

        var routerSelect = document.createElement('select');
        var routers = [
            { value: 'normal', text: 'Normal' },
            { value: 'manhattan', text: 'Manhattan' },
            { value: 'metro', text: 'Metro' },
            { value: 'orthogonal', text: 'Orthogonal' }
        ];

        routers.forEach(function(router) {
            var option = document.createElement('option');
            option.value = router.value;
            option.text = router.text;
            routerSelect.appendChild(option);
        });

        var currentRouter = '';
        if (element.get('router')) {
            currentRouter = element.get('router').name || 'normal';
        }

        routerSelect.value = currentRouter;
        routerSelect.addEventListener('change', function() {
            element.router(this.value !== 'normal' ? { name: this.value } : null);
        });
        propertiesContent.appendChild(routerSelect);
    }

    // Helper function to ensure a color string is a valid hex color
    function ensureValidColor(color) {
        if (!color || typeof color !== 'string') {
            return '#000000';
        }

        // Check if it's a valid hex color
        if (/^#[0-9A-F]{6}$/i.test(color)) {
            return color;
        }

        // Try to force to valid hex format if possible
        if (/^#[0-9A-F]{3}$/i.test(color)) {
            // Convert 3-digit hex to 6-digit hex
            return '#' + color[1] + color[1] + color[2] + color[2] + color[3] + color[3];
        }

        // Return default if all else fails
        return '#000000';
    }
}
