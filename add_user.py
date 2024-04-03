import sqlite3
import requests

conn = sqlite3.connect('players.db')
cursor = conn.cursor()

nicks = cursor.execute("SELECT * FROM players").fetchall()
for nick in nicks:
    print(nick)

nickname = input("Nickname: ")
url = f"https://open.faceit.com/data/v4/players?nickname={nickname}"
response = requests.get(url, headers={"Authorization": "Bearer 1573f37d-ed29-41b6-91d6-bf0be8846cf9"})
if response.status_code == 200:
    data = response.json()
    player_id = data['player_id']
    elo = data["games"]["cs2"]["faceit_elo"]

    cursor.execute("INSERT INTO players (id, name, elo) VALUES (?, ?, ?)", (player_id, nickname, elo))
    conn.commit()
    nicks = cursor.execute("SELECT * FROM players").fetchall()
    for nick in nicks:
        print(nick)
    conn.close()
else:
    print("Ошибка при выполнении запроса:", response.status_code)