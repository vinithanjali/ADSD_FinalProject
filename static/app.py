from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import sqlite3
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Email configuration (assuming you use Gmail with App Password)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ummadireddyvinithanjali@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'udfvnhitqafmlzzg'     # Replace with your app password
app.config['MAIL_DEFAULT_SENDER'] = 'ummadireddyvinithanjali@gmail.com'  # Replace with your email

mail = Mail(app)

# Initialize DB and create the table if it doesn't exist
def init_db():
    with sqlite3.connect('appointments.db') as conn:
        # Drop the table if it already exists (useful for re-creating the schema)
        conn.execute('DROP TABLE IF EXISTS appointments')
        
        # Create the table with the correct schema
        conn.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                doctor TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL
            );
        ''')

# Import CSV data into the database
def import_csv_to_db():
    with open('patients_dataset.csv', 'r') as file:
        reader = csv.DictReader(file)
        with sqlite3.connect('appointments.db') as conn:
            cursor = conn.cursor()
            for row in reader:
                cursor.execute('''
                    INSERT INTO appointments (name, email, doctor, date, time)
                    VALUES (?, ?, ?, ?, ?)
                ''', (row['name'], row['email'], row['doctor'], row['date'], row['time']))
            conn.commit()

# Initialize DB and import CSV
init_db()
import_csv_to_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    name = request.form['name']
    email = request.form['email']
    doctor = request.form['doctor']
    date = request.form['date']
    time = request.form['time']

    with sqlite3.connect('appointments.db') as conn:
        conn.execute('INSERT INTO appointments (name, email, doctor, date, time) VALUES (?, ?, ?, ?, ?)',
                     (name, email, doctor, date, time))

    # Send email confirmation
    msg = Message("Appointment Confirmation", recipients=[email])
    msg.body = f"Hello {name},\n\nYour appointment with Dr. {doctor} has been successfully booked on {date} at {time}.\n\nThank you!\n\n!!!See you soon!!!"
    mail.send(msg)

    flash('Appointment booked successfully! A confirmation email has been sent.')
    return redirect(url_for('appointments'))

@app.route('/appointments')
def appointments():
    with sqlite3.connect('appointments.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM appointments')
        data = cursor.fetchall()
    return render_template('appointments.html', appointments=data)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        updated = (
            request.form['name'],
            request.form['email'],
            request.form['doctor'],
            request.form['date'],
            request.form['time'],
            id
        )
        with sqlite3.connect('appointments.db') as conn:
            conn.execute('''
                UPDATE appointments 
                SET name=?, email=?, doctor=?, date=?, time=? 
                WHERE id=? 
            ''', updated)
        flash('Appointment updated successfully!')
        return redirect(url_for('appointments'))

    with sqlite3.connect('appointments.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM appointments WHERE id=?', (id,))
        appointment = cursor.fetchone()
    return render_template('edit.html', appointment=appointment)

@app.route('/delete/<int:id>')
def delete(id):
    with sqlite3.connect('appointments.db') as conn:
        conn.execute('DELETE FROM appointments WHERE id=?', (id,))
    flash('Appointment deleted successfully!')
    return redirect(url_for('appointments'))

if __name__ == '__main__':
    app.run(debug=True)
