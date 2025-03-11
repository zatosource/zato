// properties.js - Properties panel for editing elements

function setupPropertiesPanel(graph, paper) {
    var propertiesContent = document.getElementById('properties-content');
    var selectedElement = null;

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

        // Common properties
        var idLabel = document.createElement('label');
        idLabel.innerText = 'ID:';
        propertiesContent.appendChild(idLabel);

        var idInput = document.createElement('input');
        idInput.type = 'text';
        idInput.value = element.id;
        idInput.readOnly = true;
        propertiesContent.appendChild(idInput);

        // Element-specific properties
        if (!isLink) {
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

            // Fill color
            var fillLabel = document.createElement('label');
            fillLabel.innerText = 'Fill Color:';
            propertiesContent.appendChild(fillLabel);

            var fillInput = document.createElement('input');
            fillInput.type = 'color';
            fillInput.value = element.attr('body/fill') || '#FFFFFF';
            fillInput.addEventListener('change', function() {
                element.attr('body/fill', this.value);
            });
            propertiesContent.appendChild(fillInput);

            // Stroke color
            var strokeLabel = document.createElement('label');
            strokeLabel.innerText = 'Border Color:';
            propertiesContent.appendChild(strokeLabel);

            var strokeInput = document.createElement('input');
            strokeInput.type = 'color';
            strokeInput.value = element.attr('body/stroke') || '#000000';
            strokeInput.addEventListener('change', function() {
                element.attr('body/stroke', this.value);
            });
            propertiesContent.appendChild(strokeInput);

            // Width
            var widthLabel = document.createElement('label');
            widthLabel.innerText = 'Width:';
            propertiesContent.appendChild(widthLabel);

            var widthInput = document.createElement('input');
            widthInput.type = 'number';
            widthInput.min = 20;
            widthInput.max = 500;
            widthInput.value = element.get('size').width || 100;
            widthInput.addEventListener('change', function() {
                var size = element.get('size');
                element.resize(parseInt(this.value), size.height);
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
            heightInput.value = element.get('size').height || 100;
            heightInput.addEventListener('change', function() {
                var size = element.get('size');
                element.resize(size.width, parseInt(this.value));
            });
            propertiesContent.appendChild(heightInput);

            // Custom data section
            var customDataLabel = document.createElement('label');
            customDataLabel.innerText = 'Custom Data:';
            propertiesContent.appendChild(customDataLabel);

            var customDataInput = document.createElement('textarea');
            customDataInput.rows = 5;
            customDataInput.value = JSON.stringify(element.get('customData') || {}, null, 2);
            customDataInput.addEventListener('change', function() {
                try {
                    var customData = JSON.parse(this.value);
                    element.set('customData', customData);
                    this.style.borderColor = '';
                } catch (e) {
                    this.style.borderColor = 'red';
                }
            });
            propertiesContent.appendChild(customDataInput);

        } else {
            // Link properties

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
            linkColorInput.value = element.attr('line/stroke') || '#000000';
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
}
