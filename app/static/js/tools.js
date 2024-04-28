function clearOutput() {
    $('#live-results').empty(); // Empty the content of the liveResults div
}

function disableAllButtons() {
    $('button').prop('disabled', true); // Disable all buttons
}

function enableAllButtons() {
    $('button').prop('disabled', false); // Re-enable all buttons
}

function scrollToBottom(element) {
    var height = element.prop('scrollHeight');
    element.scrollTop(height); // Scroll to the bottom
}

function runScript(scriptName) {
    var liveResults = $('#live-results');

    // Disable all buttons
    disableAllButtons();

    $.ajax({
        type: 'POST',
        url: '/api/tools',
        contentType: 'application/json',
        data: JSON.stringify({ script_name: scriptName }),
        xhrFields: {
            onprogress: function (e) {
                // Append the entire response text to the liveResults div
                liveResults.html(e.currentTarget.responseText);

                // Scroll to the bottom after updating the content
                scrollToBottom(liveResults);
            },
            onerror: function (xhr, status, error) {
                console.error('Error receiving data:', error);
                liveResults.html('Error receiving data. Please try again.');

                scrollToBottom(liveResults); // Ensure scroll to bottom on error
            }
        },
        success: function (response) {
            // Display the final response in the liveResults div
            // deepcode ignore DOMXSS: Trusted enviroment
            liveResults.html(response);
            scrollToBottom(liveResults); // Scroll to bottom
            enableAllButtons(); // Re-enable all buttons
        },
        error: function (xhr, status, error) {
            console.error('Error sending request:', error);
            liveResults.html('Error sending request. Please try again.');

            scrollToBottom(liveResults); // Scroll to bottom on error
            enableAllButtons(); // Re-enable all buttons
        }
    });
}
