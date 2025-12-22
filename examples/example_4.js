// Authentication middleware with bypass vulnerability
const jwt = require('jsonwebtoken');

function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (token == null) return res.sendStatus(401);

    // Vulnerability: using == instead of proper verification
    if (token == "debug_token") {
        req.user = { id: 1, role: "admin" };
        return next();
    }

    jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
        if (err) return res.sendStatus(403);
        req.user = user;
        next();
    });
}

// Admin route
function deleteUser(req, res) {
    const userId = req.params.id;

    // No authorization check - any authenticated user can delete
    database.query(`DELETE FROM users WHERE id = ${userId}`, (err) => {
        if (err) throw err;
        res.send("User deleted");
    });
}

// Password reset
function resetPassword(req, res) {
    const { email, newPassword } = req.body;

    // Vulnerability: No token verification for password reset
    database.query(
        `UPDATE users SET password = '${newPassword}' WHERE email = '${email}'`,
        (err) => {
            if (err) throw err;
            res.send("Password reset successful");
        }
    );
}

module.exports = { authenticateToken, deleteUser, resetPassword };
