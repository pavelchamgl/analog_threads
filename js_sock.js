let token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk0NzMzOTg5LCJpYXQiOjE2OTQ3MzAzODksImp0aSI6Ijk4YjczNWNmMTFiZTQ4ZDY5MTcxZmY4NzAzNGM0NmYzIiwidXNlcl9pZCI6Mn0.FjuwIcSXpJWGuEareuVe3QkWFhXn7qE6fsyzHKgDeGE"

if ("WebSocket" in window) {
    // Replace with your server's URL e.g., 'ws://127.0.0.1:8000/ws/notifications/'
    const websocketURL = "ws://127.0.0.1:8000/ws/notifications/?token=" + token;
    const websocket = new WebSocket(websocketURL);

    // Connection is open
    websocket.onopen = function (event) {
        console.log("WebSocket connected: ", event);
    };

    // Connection has an error
    websocket.onerror = function (error) {
        console.log("WebSocket error: ", error);
    };

    // Connection is closed
    websocket.onclose = function (event) {
        console.log("WebSocket disconnected: ", event);
    };

    // Listen for messages from the server
    websocket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        const message = data.message;
        console.log("Received message: ", message);
    };

    // Send a message to the server
    function sendMessage(message) {
        const data = {
            "message": message
        };
        websocket.send(JSON.stringify(data));
    }

    // Examples: sendMessage("Hello, it's a test message!");
} else {
    console.log("Your browser does not support WebSocket.");
}