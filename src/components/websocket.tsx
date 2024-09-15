import { useEffect, useState } from 'react';

const WebSocketComponent = () => {
    const [message, setMessage] = useState('');
    const [socket, setSocket] = useState(null);

    useEffect(() => {
        // Create WebSocket connection.
        const ws = new WebSocket('ws://localhost:8000/ws');

        // Connection opened
        ws.onopen = () => {
            console.log('Connected to WebSocket');
        };

        // Listen for messages
        ws.onmessage = (event) => {
            setMessage(event.data);
            console.log('Message from server: ', event.data);
        };

        // Handle WebSocket closure
        ws.onclose = () => {
            console.log('WebSocket connection closed');
        };

        // Save the WebSocket object
        setSocket(ws);

        // Cleanup on component unmount
        return () => {
            if (ws) {
                ws.close();
            }
        };
    }, []);


    return (
        <div>
            <h1>Console</h1>
            <p>Message from server: {message}</p>
        </div>
    );
};

export default WebSocketComponent;