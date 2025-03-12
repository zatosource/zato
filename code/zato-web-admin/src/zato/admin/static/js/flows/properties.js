// properties.js - Simplified properties panel focused on core element properties

function setupPropertiesPanel(graph, paper) {
    // Get the properties content container
    const propertiesContent = document.getElementById('properties-content');
    let selectedElement = null;

    if (!propertiesContent) {
        console.error("Properties panel content element not found");
        return;
    }

    // Set up event listeners for element selection
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

    /**
     * Updates the properties panel with the selected element's properties
     * @param {Object} element - The selected JointJS element
     */
    function updatePropertiesPanel(element) {
        if (!element) return;

        // Clear the current properties
        propertiesContent.innerHTML = '';

        const isLink = element.isLink();

        // Add ID property (read-only)
        addProperty('ID:', element.id, true);

        // For elements (not links), show the core properties
        if (!isLink) {
            // Add Label property
            const label = element.attr('label/text') || '';
            addProperty('Label:', label, false, function(value) {
                element.attr('label/text', value);
            });

            // Add Fill Color property
            const fillAttr = 'body/fill';
            const fillColor = ensureValidColor(element.attr(fillAttr) || '#FFFFFF');
            addColorProperty('Fill Color:', fillColor, function(value) {
                element.attr(fillAttr, value);
            });

            // Add Border Color property
            const strokeAttr = 'body/stroke';
            const borderColor = ensureValidColor(element.attr(strokeAttr) || '#000000');
            addColorProperty('Border Color:', borderColor, function(value) {
                element.attr(strokeAttr, value);
            });

            // Add Custom Data property
            addCustomDataProperty(element);
        } else {
            // For links, only allow editing the line color
            const linkColor = ensureValidColor(element.attr('line/stroke') || '#000000');
            addColorProperty('Line Color:', linkColor, function(value) {
                element.attr('line/stroke', value);
            });
        }

        // Add Delete button
        addDeleteButton(element);
    }

    /**
     * Adds a text property to the panel
     * @param {string} label - The label for the property
     * @param {string} value - The current value
     * @param {boolean} readOnly - Whether the property is read-only
     * @param {Function} onChange - Function to call when value changes
     */
    function addProperty(label, value, readOnly = false, onChange = null) {
        // Create label element
        const labelEl = document.createElement('label');
        labelEl.innerText = label;
        propertiesContent.appendChild(labelEl);

        // Create input element
        const input = document.createElement('input');
        input.type = 'text';
        input.value = value;

        if (readOnly) {
            input.readOnly = true;
        } else if (onChange) {
            input.addEventListener('change', function() {
                onChange(this.value);
            });
        }

        propertiesContent.appendChild(input);
    }

    /**
     * Adds a color picker property to the panel
     * @param {string} label - The label for the property
     * @param {string} value - The current color value
     * @param {Function} onChange - Function to call when color changes
     */
    function addColorProperty(label, value, onChange) {
        // Create label element
        const labelEl = document.createElement('label');
        labelEl.innerText = label;
        propertiesContent.appendChild(labelEl);

        // Create color input
        const input = document.createElement('input');
        input.type = 'color';
        input.value = value;

        if (onChange) {
            input.addEventListener('change', function() {
                onChange(this.value);
            });
        }

        propertiesContent.appendChild(input);
    }

    /**
     * Adds the custom data textarea property
     * @param {Object} element - The JointJS element
     */
    function addCustomDataProperty(element) {
        // Create section label
        const sectionLabel = document.createElement('label');
        sectionLabel.innerText = 'Custom Data:';
        propertiesContent.appendChild(sectionLabel);

        // Create container for textarea and potential error message
        const container = document.createElement('div');
        container.className = 'custom-data-container';
        propertiesContent.appendChild(container);

        // Create textarea
        const textarea = document.createElement('textarea');
        textarea.rows = 5;
        textarea.value = JSON.stringify(element.get('customData') || {}, null, 2);
        container.appendChild(textarea);

        // Create error container
        const errorContainer = document.createElement('div');
        errorContainer.className = 'json-error';
        errorContainer.style.display = 'none';
        container.appendChild(errorContainer);

        // Add event listener for changes
        textarea.addEventListener('change', function() {
            try {
                // Try to parse the JSON
                const customData = JSON.parse(this.value);
                element.set('customData', customData);

                // Clear any error styling
                this.style.borderColor = '';
                errorContainer.style.display = 'none';
            } catch (e) {
                // Display error message
                this.style.borderColor = 'red';
                errorContainer.innerHTML = '<div style="color: red; font-size: 12px;">Invalid JSON: ' + e.message + '</div>';
                errorContainer.style.display = 'block';
            }
        });
    }

    /**
     * Adds a delete button for the element
     * @param {Object} element - The JointJS element
     */
    function addDeleteButton(element) {
        const deleteButton = document.createElement('button');
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

    /**
     * Ensures that a color string is a valid hex color
     * @param {string} color - The color string to validate
     * @return {string} A valid hex color
     */
    function ensureValidColor(color) {
        if (!color || typeof color !== 'string') {
            return '#000000';
        }

        // Check if it's a valid hex color
        if (/^#[0-9A-F]{6}$/i.test(color)) {
            return color;
        }

        // Try to convert 3-digit hex to 6-digit hex
        if (/^#[0-9A-F]{3}$/i.test(color)) {
            return '#' + color[1] + color[1] + color[2] + color[2] + color[3] + color[3];
        }

        // Return default if all else fails
        return '#000000';
    }
}
