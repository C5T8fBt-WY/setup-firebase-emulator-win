const functions = require('firebase-functions');

// Simple HTTP function
exports.helloWorld = functions.https.onRequest((request, response) => {
    response.send("Hello from Firebase Functions Emulator!");
});
