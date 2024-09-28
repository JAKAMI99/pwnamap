
function clearOutput() {
    $('#live-results').empty(); // Empty the content of the liveResults div
}

function disableAllButtons() {
    $('button').prop('disabled', true);
}

function enableAllButtons() {
    $('button').prop('disabled', false);
}

function scrollToBottom(element) {
    var height = element.prop('scrollHeight');
    element.scrollTop(height);
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

function uploadFile(event) {
    var file = event.target.files[0];
    if (file) {
        var formData = new FormData();
        formData.append('file', file);

        $.ajax({
            url: '/api/pot_upload',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function (response) {
                if (response.status === "success") {
                    runScript('manual_pot');
                } else {
                    $('#live-results').html(response.message);
                    enableAllButtons();
                }
            },
            error: function (xhr, status, error) {
                console.error('Error uploading file:', error);
                $('#live-results').html('Error uploading file. Please try again.');
                enableAllButtons();
            }
        });
    }
}

