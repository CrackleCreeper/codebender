const express = require('express');
const bodyParser = require('body-parser');
const CharacterAI = require('node-characterai');

const app = express();
const port = 3000; // You can choose a different port

app.use(bodyParser.json());

// Initialize the CharacterAI client (you'll need your account details)
const client = new CharacterAI();

async function initializeClient() {
    try {
        await client.authenticateAsGuest(); // Replace with your actual token
        console.log('CharacterAI client authenticated');
    } catch (error) {
        console.error('Error authenticating with CharacterAI:', error);
    }
}

initializeClient();

app.post('/chat', async (req, res) => {
    const { characterId, message } = req.body;

    if (!characterId || !message) {
        return res.status(400).json({ error: 'Missing characterId or message' });
    }

    try {
        const chat = await client.createOrContinueChat(characterId);
        const response = await chat.sendAndAwaitResponse(message);
        res.json({ response: response.text });
    } catch (error) {
        console.error('Error sending message to CharacterAI:', error);
        res.status(500).json({ error: 'Failed to get response from CharacterAI' });
    }
});

app.listen(port, () => {
    console.log(`Node.js API server listening at http://localhost:${port}`);
});