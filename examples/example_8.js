// Object manipulation with prototype pollution

function merge(target, source) {
    // Prototype pollution vulnerability
    for (let key in source) {
        if (typeof source[key] === 'object') {
            target[key] = merge(target[key] || {}, source[key]);
        } else {
            target[key] = source[key];
        }
    }
    return target;
}

function clone(obj) {
    // Unsafe clone that preserves __proto__
    return JSON.parse(JSON.stringify(obj));
}

// Vulnerable user preferences handler
class UserPreferences {
    constructor() {
        this.preferences = {};
    }

    update(userInput) {
        // No validation of keys
        this.preferences = merge(this.preferences, userInput);
    }

    get(key) {
        return this.preferences[key];
    }
}

// Regular expression DOS
function validateEmail(email) {
    // ReDoS vulnerability
    const emailRegex = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    return emailRegex.test(email);
}

// Timing attack vulnerability
function compareTokens(userToken, validToken) {
    // Not constant-time comparison
    if (userToken.length !== validToken.length) {
        return false;
    }

    for (let i = 0; i < userToken.length; i++) {
        if (userToken[i] !== validToken[i]) {
            return false;
        }
    }

    return true;
}
