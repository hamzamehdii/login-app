from flask import Flask, request, redirect, url_for, render_template_string, session

app = Flask(__name__)
app.secret_key = 'lab-secret-key'

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)