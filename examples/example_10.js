// API with rate limiting and authentication issues

const express = require('express');
const app = express();

// Hardcoded secrets
const API_KEY = 'sk-1234567890abcdef';
const ADMIN_PASSWORD = 'admin123';
const JWT_SECRET = 'my_secret_key';

// No rate limiting
app.post('/api/login', (req, res) => {
    const { username, password } = req.body;

    // Timing attack vulnerable
    if (password === ADMIN_PASSWORD) {
        res.json({ token: generateToken(username) });
    } else {
        res.status(401).send('Invalid credentials');
    }
});

// Mass assignment vulnerability
app.post('/api/users', (req, res) => {
    const user = req.body;

    // No field validation - user can set any property
    database.users.create(user);

    res.json(user);
});

// IDOR vulnerability
app.get('/api/orders/:id', (req, res) => {
    const orderId = req.params.id;

    // No ownership check
    database.query(`SELECT * FROM orders WHERE id = ${orderId}`, (err, order) => {
        res.json(order);
    });
});

// Information disclosure
app.use((err, req, res, next) => {
    // Exposes stack traces in production
    res.status(500).json({
        error: err.message,
        stack: err.stack
    });
});

// Weak session configuration
app.use(session({
    secret: 'keyboard cat',
    cookie: {
        secure: false,  // Not requiring HTTPS
        httpOnly: false  // Accessible via JavaScript
    }
}));

function generateToken(username) {
    // Predictable token generation
    return Buffer.from(username + ':' + Date.now()).toString('base64');
}
