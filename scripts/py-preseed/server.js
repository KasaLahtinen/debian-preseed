const express = require('express');
const path = require('path');
const app = express();
const PORT = 8000;

// Middleware to ensure .jsx files are served with the correct MIME type
// This is critical for the browser's native ESM loader to process them.
app.use((req, res, next) => {
    if (req.path.endsWith('.jsx')) {
        res.setHeader('Content-Type', 'text/javascript');
    }
    // Enable CORS for development flexibility
    res.setHeader('Access-Control-Allow-Origin', '*');
    next();
});

// Serve static files from the current directory
app.use(express.static(__dirname));

app.listen(PORT, () => {
    console.log('-------------------------------------------');
    console.log(`Preseed UI Demo running at: http://localhost:${PORT}`);
    console.log('-------------------------------------------');
});
