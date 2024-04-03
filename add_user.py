import sqlite3

conn = sqlite3.connect('players.db')
cursor = conn.cursor()

nicks = cursor.execute("SELECT * FROM players").fetchall()
for nick in nicks:
    print(nick)