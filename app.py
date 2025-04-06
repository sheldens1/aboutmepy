from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'luckyanjay'
app.permanent_session_lifetime = 1800  # 30 menit auto-logout
USERS_FILE = 'users.json'

# Fungsi Kirim Email saat Login
def send_login_alert(username, email_tujuan):
    pengirim = "franzackylucky@gmail.com"
    password = "sfxocchjxlmwzyvr"

    waktu = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    subjek = "Login Alert"
    isi = f"Akun '{username}' berhasil login pada {waktu}."

    msg = MIMEText(isi)
    msg['Subject'] = subjek
    msg['From'] = pengirim
    msg['To'] = email_tujuan

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(pengirim, password)
            print("Login SMTP sukses")
            server.send_message(msg)
            print(f"Email berhasil dikirim ke {email_tujuan}")
    except Exception as e:
        print("Gagal mengirim email:", e)

# Load & Simpan User
def load_users():
    if not os.path.exists(USERS_FILE) or os.stat(USERS_FILE).st_size == 0:
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        users = load_users()

        if username in users or any(user['email'] == email for user in users.values()):
            return "Username atau Email sudah terdaftar."

        if password != confirm_password:
            return "Password dan konfirmasi tidak cocok."

        users[username] = {
            'email': email,
            'password': password,
            'online': False
        }

        save_users(users)
        return redirect(url_for('login'))

    return render_template('register.html')

# Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()

        if username in users and users[username]['password'] == password:
            session.permanent = True
            session['username'] = username
            users[username]['online'] = True
            save_users(users)

            send_login_alert(username, users[username]['email'])

            return redirect(url_for('dashboard'))
        else:
            return "Username atau password salah."

    return render_template('index.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session.get('username')
    return render_template("dashboard.html", username=username)

@app.route('/lobi')
def lobi():
    return render_template('buat/lobi.html')

# Pengguna Online
@app.route('/pengguna')
def pengguna_online():
    users = load_users()
    online_users = [u for u, d in users.items() if d.get('online')]
    return render_template("pengguna.html", online_users=online_users)
# Logout
@app.route('/logout')
def logout():
    users = load_users()
    if 'username' in session:
        username = session['username']
        users[username]['online'] = False
        save_users(users)
        session.pop('username')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
