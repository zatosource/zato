// export.js - Export functionality (JSON/PNG)

function setupExport(graph) {
    // Export as JSON
    document.getElementById('export-json').addEventListener('click', function() {
        var jsonObject = graph.toJSON();

        // Prepare cleaned version of the workflow
        var exportObject = {
            version: '1.0',
            metadata: {
                title: 'Workflow Export',
                date: new Date().toISOString(),
                author: 'No-Code Workflow Editor'
            },
            graph: jsonObject
        };

        var jsonString = JSON.stringify(exportObject, null, 2);
        downloadFile('workflow.json', jsonString, 'application/json');
    });

    // Export as PNG
    document.getElementById('export-png').addEventListener('click', function() {
        // Convert SVG to canvas and then to PNG
        var svgElement = document.querySelector('#paper svg');

        if (!svgElement) {
            alert('No diagram to export');
            return;
        }

        var serializer = new XMLSerializer();
        var svgString = serializer.serializeToString(svgElement);

        // Create a canvas element
        var canvas = document.createElement('canvas');
        var context = canvas.getContext('2d');

        // Set canvas dimensions to match the SVG
        var svgRect = svgElement.getBoundingClientRect();
        canvas.width = svgRect.width;
        canvas.height = svgRect.height;

        // Create an image from the SVG
        var image = new Image();
        image.onload = function() {
            // Fill canvas with white background
            context.fillStyle = 'white';
            context.fillRect(0, 0, canvas.width, canvas.height);

            // Draw the image onto the canvas
            context.drawImage(image, 0, 0);

            // Convert canvas to data URL and download
            var pngData = canvas.toDataURL('image/png');
            downloadFile('workflow.png', pngData, 'image/png', true);
        };

        // Convert SVG to data URL
        image.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgString)));
    });

    // Helper function to download a file
    function downloadFile(filename, data, type, isDataURL) {
        var link = document.createElement('a');
        link.download = filename;

        if (isDataURL) {
            link.href = data;
        } else {
            var blob = new Blob([data], {type: type});
            link.href = window.URL.createObjectURL(blob);
        }

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}
