import sqlite3
import requests
from flask import Flask, request

app = Flask(__name__)


def get_users():
    nicknames = []
    conn = sqlite3.connect('players.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS players (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        elo INTEGER
                    )''')
    nicks = cursor.execute("SELECT name FROM players").fetchall()
    for nick in nicks:
        nicknames.append(nick[0])

    conn.commit()
    conn.close()
    return nicknames


def refresh_elo(id, elo):
    conn = sqlite3.connect('players.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET elo = ? WHERE id = ?", (elo, id))
    conn.commit()
    conn.close()


def get_elo(id):
    conn = sqlite3.connect('players.db')
    cursor = conn.cursor()
    elo = cursor.execute("SELECT elo FROM players WHERE id = ?", (id,)).fetchone()
    conn.commit()
    conn.close()
    return elo[0]


@app.route('/receive_post', methods=['POST'])
def receive_post():
    if request.method == 'POST':
        data = request.get_json()
        print("Получен POST запрос\n")
        main(data)

        return "POST запрос успешно получен и обработан"
    else:
        return "Метод не поддерживается"


def get_info(name):
    url = f"https://open.faceit.com/data/v4/players?nickname={name}"
    response = requests.get(url, headers={"Authorization": "Bearer 1573f37d-ed29-41b6-91d6-bf0be8846cf9"})
    if response.status_code == 200:
        data = response.json()
        player_id = data['player_id']
        elo = data["games"]["cs2"]["faceit_elo"]
        url1 = f"https://open.faceit.com/data/v4/players/{player_id}/games/cs2/stats?offset=0&limit=1"
        response1 = requests.get(url1, headers={"Authorization": "Bearer 1573f37d-ed29-41b6-91d6-bf0be8846cf9"})
        if response1.status_code == 200:
            data = response1.json()
            stats = data['items'][0]['stats']
            kd = stats['K/D Ratio']
            kr = stats['K/R Ratio']
            kills = stats['Kills']
            death = stats['Deaths']
            last_elo = get_elo(player_id)
            elo_per_match = int(elo) - int(last_elo)

            refresh_elo(player_id, elo)

            print("NICKNAME:", name)
            print("LAST ELO:", last_elo)
            print("ELO PER MATCH:", elo_per_match)
            print("ELO NOW:", elo)
            print("\n")
            print("K/D Ratio:", kd)
            print("K/R Ratio:", kr)
            print("Kills:", kills)
            print("Deaths:", death)
            print("\n")

    else:
        print("Ошибка при выполнении запроса:", response.status_code)


def main(data):
    if data["event"] == "match_status_finished":
        for d in data["payload"]["teams"]:
            for a in d['roster']:
                if a['nickname'] in get_users():
                    get_info(a['nickname'])


if __name__ == '__main__':
    app.run(debug=True)
