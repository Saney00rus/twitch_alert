import sqlite3
import requests
from flask import Flask, request, render_template
from flask_socketio import SocketIO
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

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


def send_data_to_frontend(data):
    socketio.emit('update_data', data)


@app.route('/receive_post', methods=['POST'])
def receive_post():
    if request.method == 'POST':
        data = request.get_json()
        print("Получен POST запрос\n")
        main(data)

        return "POST запрос успешно получен и обработан"
    else:
        return "Метод не поддерживается"


@app.route('/<nickname>')
def player_stats(nickname):
    if request.method == 'GET':
        data_to_send = get_info(nickname)
        return render_template('player_stats.html', playerData=data_to_send)



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

            data_to_send = {
                'nickname': name,
                'player_id': player_id,
                'last_elo': str(last_elo),
                'elo_per_match': str(elo_per_match),
                'elo_now': str(elo),
                'kd_ratio': kd,
                'kr_ratio': kr,
                'kills': kills,
                'deaths': death
            }

            return data_to_send
    else:
        print("Ошибка при выполнении запроса:", response.status_code)

def prnt_res(res):
    name = res['nickname']
    last_elo = res['last_elo']
    elo_per_match = res['elo_per_match']
    elo = res['elo_now']
    kd = res['kd_ratio']
    kr = res['kr_ratio']
    kills = res['kills']
    death = res['deaths']

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


def main(data):
    if data["event"] == "match_status_finished":
        for d in data["payload"]["teams"]:
            for a in d['roster']:
                if a['nickname'] in get_users():
                    res = get_info(a['nickname'])
                    id = res['player_id']
                    elo = res['elo_now']
                    refresh_elo(id, elo)
                    send_data_to_frontend(res)
                    prnt_res(res)


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    app.run(debug=True)
