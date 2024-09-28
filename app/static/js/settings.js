document.addEventListener('DOMContentLoaded', function() {
    // Get credentials from creds.txt and populate the form
    fetch('/api/credentials')
        .then(response => response.json())
        .then(data => {
            document.getElementById('wigle').value = data.wigle;
            document.getElementById('wpasec').value = data.wpasec
            document.getElementById('pwnamap').value = data.pwnamap;
        })
        .catch(error => console.error('Error fetching credentials:', error));

    // Handle form submission
    document.getElementById('credentials-form').addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(this);

        // Send credentials to the server
        fetch('/api/credentials', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(Object.fromEntries(formData))
        })
        .then(response => {
            if (response.ok) {
                document.getElementById('feedback').textContent = 'Saved';
            } else {
                throw new Error('Failed to save credentials');
            }
        })
        .catch(error => console.error('Error saving credentials:', error));
        

    });

});
