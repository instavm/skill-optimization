# User Authentication System
# This code has multiple security and quality issues

import sqlite3
import hashlib

def authenticate_user(username, password):
    # Connect to database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Check user credentials
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    cursor.execute(query)
    result = cursor.fetchone()

    if result:
        return True
    return False

def create_user(username, password, email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Hash the password
    hashed = hashlib.md5(password.encode()).hexdigest()

    query = f"INSERT INTO users VALUES ('{username}', '{hashed}', '{email}')"
    cursor.execute(query)
    conn.commit()

    return True

def get_user_data(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchone()

def delete_user(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = '" + username + "'")
    conn.commit()

# API endpoint
def login_api(request):
    username = request.GET.get('username')
    password = request.GET.get('password')

    if authenticate_user(username, password):
        return {"status": "success", "message": "Login successful"}
    else:
        return {"status": "error", "message": "Invalid credentials"}
