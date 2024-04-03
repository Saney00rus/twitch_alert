import datetime
import sqlite3
import requests
from flask import Flask, request

app = Flask(__name__)



def get_users():

    nicknames = []
    # Подключение к базе данных (если базы данных не существует, она будет создана)
    conn = sqlite3.connect('players.db')

    # Создание курсора для выполнения SQL-запросов
    cursor = conn.cursor()

    # Создание таблицы players с тремя столбцами: id, name, elo
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


@app.route('/receive_post', methods=['POST'])
def receive_post():
    if request.method == 'POST':
        data = request.get_json()
        print("\nПолучен POST запрос\n")
        print(data)
        print("\n\n")
        print(main(data))

        return "POST запрос успешно получен и обработан"
    else:
        return "Метод не поддерживается"

@app.route('/<nickname>', methods=['GET'])
def show_stats(nickname):
    if nickname in get_users():
        res = get_info(nickname)
        return prnt_res(res)
    else:
        return "Нет данных для этого никнейма"


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
            print("ELO:", elo)
            print("K/D Ratio:", kd)
            print("K/R Ratio:", kr)
            print("Kills:", kills)
            print("Deaths:", death)



    else:
        print("Ошибка при выполнении запроса:", response.status_code)


def prnt_res(res):
    elo = res['elo']
    last_elo = res['last_elo']
    elo_match = res['elo_match']
    kill = res['kill']
    deaths = res['deaths']
    kd = res['kd']
    kr = res['kr']

    return (f'{datetime.datetime.now()}\n'
            f'LAST ELO: {last_elo} elo \n'
            f'ELO PER GAME: {elo_match} elo\n'
            f'NEW ELO: {elo} elo\n\n'
            f'KILL: {kill}\n'
            f'DEATHS: {deaths}\n'
            f'K/D: {kd}\n'
            f'K/R: {kr}\n')


def main(data):
    if data["event"] == "match_status_finished":
        for d in data["payload"]["teams"]:
            for a in d['roster']:
                if a['nickname'] in get_users():
                    res = get_info(a['nickname'])
                    # return prnt_res(res)


if __name__ == '__main__':
    app.run(debug=True)
