import datetime

import requests
from flask import Flask, request
import re

app = Flask(__name__)

nicknames = ['anastazecs',]


@app.route('/receive_post', methods=['POST'])
def receive_post():
    if request.method == 'POST':
        data = request.get_json()
        print("\nПолучен POST запрос\n")
        print(main(data))

        return "POST запрос успешно получен и обработан"
    else:
        return "Метод не поддерживается"

@app.route('/<nickname>', methods=['GET'])
def show_stats(nickname):
    if nickname in nicknames:
        res = get_info(nickname)
        return prnt_res(res)
    else:
        return "Нет данных для этого никнейма"

def get_info(name):
    url = f"http://api.faceit.myhosting.info:81/?n={name}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        last_match = data['last_match']
        elo = data["elo"]
        elo_match = last_match.split()[13]
        last_elo = int(elo) - int(elo_match)
        kill = last_match.split()[5].split('/')[0]
        deaths = last_match.split()[5].split('/')[2]
        kd = last_match.split()[7]
        kr1 = re.sub(r"[(),]", "", last_match.split()[3]).split(":")
        kr = round(int(kill) / (int(kr1[0]) + int(kr1[1])), 2)

        res = {'nickname': name, 'last_elo': last_elo, 'elo': elo, 'elo_match': elo_match, 'kill': kill,
               'deaths': deaths, 'kd': kd, 'kr': kr}
        return res

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
                if a['nickname'] in nicknames:
                    res = get_info(a['nickname'])
                    return prnt_res(res)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
