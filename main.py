from base64 import urlsafe_b64encode
from flask import Flask, g, make_response, redirect, render_template, request, session, url_for
from io import StringIO
from random import uniform as random_float
from sys import exit
import csv
import sqlite3


DATABASE = 'democracy.db'
app = Flask(__name__)
app.secret_key = b'dsadsadsa dsadsad cxzcxz opgkrwegpwfepqm'

# generate random bytes and then URL-safe Base64 encode them
def generate_unique_id(length=15):
    id = bytearray()
    for i in range(length):
        id.append(int(random_float(0,255)))
    return urlsafe_b64encode(id).decode("ASCII")

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def initialize_database():
    sql_cursor = get_db().cursor()
    sql_cursor.execute('CREATE TABLE polls (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT NOT NULL, open BOOLEAN NOT NULL DEFAULT 1)')
    sql_cursor.execute('CREATE TABLE poll_options (id INTEGER PRIMARY KEY AUTOINCREMENT, poll_id INTEGER NOT NULL, value TEXT NOT NULL, FOREIGN KEY(poll_id) REFERENCES polls(id))')
    sql_cursor.execute('CREATE TABLE results_hashes (poll_id INTEGER PRIMARY KEY, poll_option_id INTEGER NOT NULL, hash TEXT NOT NULL, FOREIGN KEY(poll_option_id) REFERENCES poll_options(id))')
    sql_cursor.execute('CREATE TABLE voters (id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL, ssn INTEGER NOT NULL)')
    sql_cursor.execute('CREATE TABLE votes (id TEXT PRIMARY KEY, voter_id INTEGER NOT NULL, poll_id INTEGER NOT NULL, poll_option_id INTEGER NOT NULL, FOREIGN KEY(voter_id) REFERENCES voters(id), FOREIGN KEY(poll_id) REFERENCES polls(id), FOREIGN KEY(poll_option_id) REFERENCES poll_options(id))')
    sql_cursor.execute('INSERT INTO polls (title, description, open) VALUES ("A frog in every home?", "Proposition would mandate that for every home there is a frog, and for every frog there is a home.", 0)')
    sql_cursor.execute('INSERT INTO polls (title, description, open) VALUES ("Human rights for animals?", "Proposition would make animals a protected class on the basis of species.", 0)')
    sql_cursor.execute('INSERT INTO polls (title, description) VALUES ("New name for Portland?", "Ballot decides Portland\'s new name after humanity meets its amphibious end.")')
    sql_cursor.execute('INSERT INTO poll_options (poll_id, value) VALUES (1, "Yes")')
    sql_cursor.execute('INSERT INTO poll_options (poll_id, value) VALUES (1, "No")')
    sql_cursor.execute('INSERT INTO poll_options (poll_id, value) VALUES (2, "Yes")')
    sql_cursor.execute('INSERT INTO poll_options (poll_id, value) VALUES (2, "No")')
    sql_cursor.execute('INSERT INTO poll_options (poll_id, value) VALUES (3, "Poleland")')
    sql_cursor.execute('INSERT INTO poll_options (poll_id, value) VALUES (3, "Toad Town")')
    sql_cursor.execute('INSERT INTO results_hashes (poll_id, poll_option_id, hash) VALUES (1, 1, "897a1802bcc42400231ff6ff6d7777fd35a706bbd295033d3818be7b2d6c0721")')
    sql_cursor.execute('INSERT INTO results_hashes (poll_id, poll_option_id, hash) VALUES (2, 3, "388b5038e406ec73a3135c795fc9b24437bf318e04b9ae3618125e5417166e62")')
    sql_cursor.execute('INSERT INTO voters (full_name, ssn) VALUES ("Frog Howard", "123-45-6789")')
    sql_cursor.execute('INSERT INTO voters (full_name, ssn) VALUES ("Pistol Pete", "123-45-6785")')
    sql_cursor.execute('INSERT INTO voters (full_name, ssn) VALUES ("Amphyb Ian", "123-45-6783")')
    sql_cursor.execute('INSERT INTO voters (full_name, ssn) VALUES ("Nicolas Sarkozy", "133-43-6733")')
    sql_cursor.execute('INSERT INTO votes (id, voter_id, poll_id, poll_option_id) VALUES ("YDSAD356ZvcvdDAK", 2, 1, 1)')
    sql_cursor.execute('INSERT INTO votes (id, voter_id, poll_id, poll_option_id) VALUES ("nbvrGWG22SDzxvK", 3, 1, 2)')
    sql_cursor.execute('INSERT INTO votes (id, voter_id, poll_id, poll_option_id) VALUES ("QDiojdQklmvmqn281z", 4, 1, 1)')
    sql_cursor.execute('INSERT INTO votes (id, voter_id, poll_id, poll_option_id) VALUES ("Dz32lZ11MnalLkK", 2, 2, 3)')
    sql_cursor.execute('INSERT INTO votes (id, voter_id, poll_id, poll_option_id) VALUES ("Xz36kXX752a5L1kK", 3, 2, 3)')
    sql_cursor.execute('INSERT INTO votes (id, voter_id, poll_id, poll_option_id) VALUES ("cBnZqSQD28ozlx4", 4, 2, 4)')
    sql_cursor.execute('INSERT INTO votes (id, voter_id, poll_id, poll_option_id) VALUES ("IOqdondd19ndNDSk", 2, 3, 5)')
    sql_cursor.execute('INSERT INTO votes (id, voter_id, poll_id, poll_option_id) VALUES ("DS12367inglngNIQ", 3, 3, 6)')
    get_db().commit()

def logged_in():
    return 'voter_id' in session

@app.route('/')
def index():
    if not logged_in():
        return redirect(url_for('login'))
    return redirect(url_for('get_polls'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # no validation of user identity for this demo, just log them in
        session['voter_id'] = 1
        session['votes'] = []
        return redirect(url_for('get_polls'))
    else:
        return render_template('login.html')

@app.route('/polls')
def get_polls():
    if not logged_in():
        return redirect(url_for('login'))
    sql_cursor = get_db().cursor()
    sql_cursor.execute('SELECT * FROM polls')
    polls = sql_cursor.fetchall()
    sql_cursor.execute('SELECT results_hashes.poll_id, results_hashes.hash, poll_options.value AS result FROM results_hashes, poll_options WHERE results_hashes.poll_option_id = poll_options.id')
    hashes = {}
    for row in sql_cursor.fetchall():
        hashes[row['poll_id']] = row
    return render_template('polls.html', polls_voted_in=session['votes'], polls=polls, hashes=hashes)

@app.route('/votes/<int:poll_id>')
def get_votes(poll_id):
    if not logged_in():
        return redirect(url_for('login'))
    sql_cursor = get_db().cursor()
    sql_cursor.execute('SELECT votes.id, votes.poll_id, poll_options.value FROM votes, poll_options WHERE votes.poll_id = ? AND votes.poll_option_id = poll_options.id', (poll_id,))
    votes = sql_cursor.fetchall()
    # build a CSV file for the user to download
    buffer = StringIO()
    csv_writer = csv.DictWriter(buffer, fieldnames=['id', 'poll_id', 'value'], extrasaction='ignore')
    csv_writer.writeheader()
    for vote in votes:
        csv_writer.writerow(dict(vote))
    csv_contents = buffer.getvalue()
    output = make_response(csv_contents)
    output.headers["Content-Disposition"] = f"attachment; filename=poll_results_{poll_id}.csv"
    output.headers["Content-Type"] = "text/csv"
    return output
   
@app.route('/vote/<int:poll_id>', methods=['GET', 'POST'])
def cast_vote(poll_id):
    if not logged_in():
        return redirect(url_for('login'))
    if poll_id in session['votes']:
        return "You already voted in this poll. Go back."
    sql = get_db()
    sql_cursor = sql.cursor()
    if request.method == 'POST':
        # sanity check poll_option_id submitted by user
        chosen_option = request.form['poll_option_id']
        sql_cursor.execute('SELECT COUNT(id) AS count from poll_options WHERE poll_id = ? AND id = ?', (poll_id, chosen_option))
        count = sql_cursor.fetchone()['count']
        if count == 0:
            return "Invalid poll option selected."
        # end sanity check. insert into database
        unique_id = generate_unique_id()
        vote_values = (unique_id, session['voter_id'], poll_id, chosen_option)
        sql_cursor.execute('INSERT INTO votes(id, voter_id, poll_id, poll_option_id) VALUES (?, ?, ?, ?)', vote_values)
        sql.commit()
        session['votes'].append(poll_id)
        # modifications to mutable objects are not automatically detected by Flask
        session.modified = True
        return render_template('voted.html', poll_id=poll_id, vote_id=unique_id)
    else:
        sql_cursor.execute('SELECT title, description FROM polls WHERE id = ?', (poll_id,))
        poll = sql_cursor.fetchone()
        sql_cursor.execute('SELECT id, value FROM poll_options WHERE poll_id = ?', (poll_id,))
        poll_options = sql_cursor.fetchall()
        return render_template('vote.html', poll=poll, poll_options=poll_options)

if __name__ == "__main__":
    app.debug = True
    # check whether the SQLite database has been created properly already
    with app.app_context():
        try:
            get_db().cursor().execute('SELECT * FROM polls')
        except sqlite3.OperationalError as e:
            initialize_database()
    app.run()