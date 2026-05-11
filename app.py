from flask import Flask, request, redirect, url_for, render_template_string, session, jsonify

app = Flask(__name__)
app.secret_key = 'lab-secret-key'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False 

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

USERS = {'admin': 'password123', 'user': 'test456'}

LOGIN_HTML = '''
<!DOCTYPE html><html><body>
<h2>Login</h2>
<form method="POST">
  Username: <input name="username"><br>
  Password: <input name="password" type="password"><br>
  <input type="submit" value="Login">
</form>
{% if error %}<p style="color:red">{{ error }}</p>{% endif %}
</body></html>'''

DASHBOARD_HTML = '''
<!DOCTYPE html><html><body>
<h2>Welcome, {{ user }}!</h2>
<p>You are logged in.</p>
<a href="/logout">Logout</a>
</body></html>'''

@app.route('/', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        if u in USERS and USERS[u] == p:
            session['user'] = u
            return redirect(url_for('dashboard'))
        error = 'Invalid credentials'
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template_string(DASHBOARD_HTML, user=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON body provided'}), 400
    u = data.get('username', '')
    p = data.get('password', '')
    if u in USERS and USERS[u] == p:
        return jsonify({'status': 'success', 'message': f'Welcome {u}', 'user': u}), 200
    return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

@app.route('/api/users', methods=['GET'])
def api_users():
    return jsonify({'users': list(USERS.keys())}), 200

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({'status': 'healthy', 'app': 'login-app'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)