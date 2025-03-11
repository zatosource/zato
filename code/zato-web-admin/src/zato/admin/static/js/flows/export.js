// export.js - Export functionality (JSON/PNG)

function setupExport(graph) {
    // Export as JSON
    const exportJsonButton = document.getElementById('export-json');
    if (exportJsonButton) {
        exportJsonButton.addEventListener('click', function() {
            try {
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
            } catch (error) {
                console.error('Error exporting JSON:', error);
                alert('Failed to export as JSON: ' + error.message);
            }
        });
    }

    // Export as PNG
    const exportPngButton = document.getElementById('export-png');
    if (exportPngButton) {
        exportPngButton.addEventListener('click', function() {
            try {
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

                // Ensure dimensions are positive and reasonable
                if (svgRect.width <= 0 || svgRect.height <= 0 ||
                    !isFinite(svgRect.width) || !isFinite(svgRect.height)) {
                    alert('Cannot export diagram with invalid dimensions');
                    return;
                }

                canvas.width = svgRect.width;
                canvas.height = svgRect.height;

                // Create an image from the SVG
                var image = new Image();

                // Set up error handling
                image.onerror = function(error) {
                    console.error('Error loading SVG for export:', error);
                    alert('Failed to convert diagram to PNG. Please try again or use another export format.');
                };

                image.onload = function() {
                    try {
                        // Fill canvas with white background
                        context.fillStyle = 'white';
                        context.fillRect(0, 0, canvas.width, canvas.height);

                        // Draw the image onto the canvas
                        context.drawImage(image, 0, 0);

                        // Convert canvas to data URL and download
                        try {
                            var pngData = canvas.toDataURL('image/png');
                            downloadFile('workflow.png', pngData, 'image/png', true);
                        } catch (e) {
                            console.error('Canvas export error:', e);
                            alert('Failed to generate PNG. The diagram might contain elements that cannot be exported.');
                        }
                    } catch (error) {
                        console.error('Error rendering PNG:', error);
                        alert('Failed to render the PNG. Please try again.');
                    }
                };

                // Convert SVG to data URL - use the simpler, more reliable approach
                try {
                    // Add a namespace if it doesn't have one (helps with some browsers)
                    if (!svgString.match(/^<svg[^>]+xmlns="http:\/\/www\.w3\.org\/2000\/svg"/)) {
                        svgString = svgString.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
                    }

                    // Add width and height attributes if they're missing
                    if (!svgString.match(/^<svg[^>]+width/)) {
                        svgString = svgString.replace(/^<svg/, `<svg width="${svgRect.width}"`);
                    }

                    if (!svgString.match(/^<svg[^>]+height/)) {
                        svgString = svgString.replace(/^<svg/, `<svg height="${svgRect.height}"`);
                    }

                    var encoded = btoa(unescape(encodeURIComponent(svgString)));
                    image.src = 'data:image/svg+xml;base64,' + encoded;
                } catch (e) {
                    console.error('SVG encoding error:', e);
                    alert('Error encoding the diagram. Some special characters might not be supported.');
                }
            } catch (error) {
                console.error('Error in PNG export:', error);
                alert('Export to PNG failed: ' + error.message);
            }
        });
    }

    // Helper function to download a file
    function downloadFile(filename, data, type, isDataURL) {
        try {
            var link = document.createElement('a');
            link.download = filename;

            if (isDataURL) {
                link.href = data;
            } else {
                var blob = new Blob([data], {type: type});
                var objectUrl = window.URL.createObjectURL(blob);
                link.href = objectUrl;
            }

            // Use a more browser-compatible approach
            if (document.createEvent) {
                var event = document.createEvent('MouseEvents');
                event.initEvent('click', true, true);
                link.dispatchEvent(event);
            } else {
                // Append to body and click
                document.body.appendChild(link);
                link.click();

                // Clean up
                setTimeout(function() {
                    if (link.parentNode) {
                        document.body.removeChild(link);
                    }

                    if (!isDataURL && objectUrl) {
                        window.URL.revokeObjectURL(objectUrl); // Free memory
                    }
                }, 200); // Increased timeout for slower systems
            }
        } catch (error) {
            console.error('Download error:', error);
            alert('Failed to download file: ' + error.message);
        }
    }
}
