// Web application with XSS and CSRF vulnerabilities

function displayUserComment(comment) {
    // XSS vulnerability - directly inserting user input
    document.getElementById('comments').innerHTML += `
        <div class="comment">
            <p>${comment.text}</p>
            <small>Posted by ${comment.author}</small>
        </div>
    `;
}

function searchProducts(query) {
    // Reflected XSS in search
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `<h2>Search results for: ${query}</h2>`;

    fetch(`/api/search?q=${query}`)
        .then(res => res.json())
        .then(data => {
            data.forEach(product => {
                resultsDiv.innerHTML += `<div>${product.name}</div>`;
            });
        });
}

// CSRF vulnerable - no token validation
function updateProfile(formData) {
    fetch('/api/profile/update', {
        method: 'POST',
        body: JSON.stringify(formData)
    }).then(res => {
        alert('Profile updated!');
    });
}

// DOM-based XSS
function loadPage() {
    const page = location.hash.substring(1);
    document.getElementById('content').innerHTML = decodeURIComponent(page);
}

// Insecure randomness for security token
function generateSessionId() {
    return Math.random().toString(36).substring(7);
}
