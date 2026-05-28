import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'pristinepalace2026secretkey'

USERS_FILE = 'users.json'
BOOKINGS_FILE = 'bookings.json'

# ⚠️ CHANGE THIS PASSWORD!
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'palace2026'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE) as f:
            return json.load(f)
    return []

def save_bookings(bookings):
    with open(BOOKINGS_FILE, 'w') as f:
        json.dump(bookings, f)

@app.route('/')
def home():
    return render_template('index.html', user=session.get('user'))

@app.route('/rooms')
def rooms():
    return render_template('rooms.html', user=session.get('user'))

@app.route('/gallery')
def gallery():
    return render_template('gallery.html', user=session.get('user'))

@app.route('/restaurant')
def restaurant():
    return render_template('restaurant.html', user=session.get('user'))

@app.route('/contact')
def contact():
    return render_template('contact.html', user=session.get('user'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        users = load_users()
        if email in users:
            flash('Email already registered!', 'error')
            return render_template('signup.html')
        users[email] = {'name': name, 'password': password}
        save_users(users)
        session['user'] = name
        session['email'] = email
        flash('Account created successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()
        if email in users and users[email]['password'] == password:
            session['user'] = users[email]['name']
            session['email'] = email
            flash('Welcome back!', 'success')
            return redirect(url_for('home'))
        flash('Invalid email or password!', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/book', methods=['GET', 'POST'])
def book():
    if not session.get('user'):
        flash('Please login to book a room!', 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        booking = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S'),
            'name': session['user'],
            'email': session['email'],
            'room': request.form['room'],
            'checkin': request.form['checkin'],
            'checkout': request.form['checkout'],
            'guests': request.form['guests'],
            'requests': request.form.get('requests', ''),
            'status': 'Confirmed',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        bookings = load_bookings()
        bookings.append(booking)
        save_bookings(bookings)
        flash('Booking confirmed! We will contact you soon.', 'success')
        return redirect(url_for('dashboard'))
    room = request.args.get('room', '')
    return render_template('book.html', user=session.get('user'), selected_room=room)

@app.route('/dashboard')
def dashboard():
    if not session.get('user'):
        return redirect(url_for('login'))
    bookings = [b for b in load_bookings() if b['email'] == session.get('email')]
    return render_template('dashboard.html', user=session.get('user'), bookings=bookings)

# ===== ADMIN ROUTES =====

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin'):
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        flash('Wrong username or password!', 'error')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    users = load_users()
    bookings = load_bookings()
    # Stats
    total_users = len(users)
    total_bookings = len(bookings)
    rooms_count = {}
    for b in bookings:
        rooms_count[b['room']] = rooms_count.get(b['room'], 0) + 1
    return render_template('admin_dashboard.html',
        users=users,
        bookings=bookings,
        total_users=total_users,
        total_bookings=total_bookings,
        rooms_count=rooms_count
    )

@app.route('/admin/booking/delete/<booking_id>')
def delete_booking(booking_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    bookings = load_bookings()
    bookings = [b for b in bookings if b.get('id') != booking_id]
    save_bookings(bookings)
    flash('Booking deleted!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
