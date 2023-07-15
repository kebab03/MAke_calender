from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import calendar
from datetime import datetime

app = Flask(__name__)

# Database connection
conn = sqlite3.connect('events.db')
cursor = conn.cursor()

# Create events table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE,
        event TEXT
    )
''')
conn.commit()

@app.route('/')
@app.route('/<int:month>/<int:year>')
def index(month=None, year=None):
    if not month or not year:
        current_date = datetime.now()
        month = current_date.month
        year = current_date.year

    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    date = f'{year}-{month:02d}-01'
    cursor.execute('SELECT date, event FROM events WHERE strftime("%Y-%m", date) = ?', (f'{year}-{month:02d}',))
    events = cursor.fetchall()

    event_data = {}
    for row in events:
        date = row[0]
        event = row[1]
        if date in event_data:
            event_data[date].append(event)
        else:
            event_data[date] = [event]

    calendar_rows = []
    numDays = calendar.monthrange(year, month)[1]

    dayCounter = 1
    for _ in range(5):
        row = []
        for _ in range(7):
            if dayCounter <= numDays:
                date = f'{year}-{month:02d}-{dayCounter:02d}'
                if date in event_data:
                    day_data = event_data[date]
                else:
                    day_data = []
                row.append((date, day_data))
                dayCounter += 1
            else:
                row.append(('', []))
        calendar_rows.append(row)

    return render_template('newind.html', calendar_rows=calendar_rows)

@app.route('/addevent', methods=['POST'])
def add_event():
    date = request.form['date']
    event = request.form['event']
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    # Remove leading zero from the month component
    year, month, day = date.split('-')
    month = str(int(month))

    # Join the date parts back together
    formatted_date = '-'.join([year, month, day])

    # Insert event into the database
    cursor.execute('INSERT INTO events (date, event) VALUES (?, ?)', (formatted_date, event))
    conn.commit()

    # Get the month and year from the date
    year, month, _ = formatted_date.split('-')

    return redirect(url_for('index', month=int(month), year=int(year)))



'''
@app.route('/addevent', methods=['POST'])
def add_event():
    date = request.form['date']
    event = request.form['event']
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    # Insert event into the database
    cursor.execute('INSERT INTO events (date, event) VALUES (?, ?)', (date, event))
    conn.commit()

    # Get the month and year from the date
    year, month, _ = date.split('-')
    print("date ,  event ", date , event)
    return redirect(url_for('index', month=int(month), year=int(year)))
'''
@app.route('/getallevents', methods=['GET'])
def get_all_events():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    cursor.execute('SELECT date, event FROM events')
    events = cursor.fetchall()

    event_data = {}
    for row in events:
        date = row[0]
        event = row[1]
        if date in event_data:
            event_data[date].append(event)
        else:
            event_data[date] = [event]

    return jsonify({'events': event_data})

if __name__ == '__main__':
    app.run()
