import argparse
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup
from openpyxl import load_workbook

import json

try:
    from config import config
except ImportError:
    from config_default import config

url_json = 'https://lk.samgtu.ru/api/common/distancelearning'
url_login = 'https://lk.samgtu.ru/site/login'
url_for_num = 'https://lk.samgtu.ru/distancelearning/distancelearning/index'


def fix_headers(filename, sheetname):
    wb = load_workbook(filename)
    sheet = wb[sheetname]

    for col in sheet.columns:
        col[0].style = 'Pandas'

    wb.save(filename)


def parse(params, headers):
    r = requests.get(url_json, params=params, headers=headers)
    if r.status_code != 200:
        print('Произошла ошибка, попробуйте проверить данные')
        return None

    req_for_name = requests.get(url_for_num, params=params, headers=headers)
    soup = BeautifulSoup(req_for_name.text, 'html.parser')
    info = soup.find('div', class_='current-user__info').text.split(' ')[-1]

    old_data = r.json()
    new_data = []

    for urok in old_data:
        name = urok['title']
        date = urok['start'].split('T')[0]
        year = date.split('-')[0]
        month = date.split('-')[1]
        day = date.split('-')[2]
        time_start = urok['start'].split('T')[1]
        time_end = urok['end'].split('T')[1]
        try:
            teacher = urok['description'].split('br')[1][1:-1]
        except IndexError:
            teacher = ""
        try:
            urok_type = urok['description'].split('br')[2][9:-10]
        except IndexError:
            urok_type = ""

        new_data.append({'Название': name,
                         'День': day,
                         'Месяц': month,
                         'Год': year,
                         'Начало': time_start,
                         'Конец': time_end,
                         'Преподаватель': teacher,
                         'Тип предмета': urok_type})

    if not os.path.isdir('json'): os.mkdir('json')
    if not os.path.isdir('xlsx'): os.mkdir('xlsx')

    # json
    with open(f"json/data_{info}.json", "w", encoding='utf-8') as json_file:
        json.dump(new_data, json_file)

    file_xlsx = f'xlsx/расписание_{info}.xlsx'
    df = pd.DataFrame(new_data)
    df.to_excel(file_xlsx, index=False)

    sheetname = 'Sheet1'
    fix_headers(file_xlsx, sheetname)

    return new_data


def main():
    params = config['params']
    headers = config['headers']

    parser = argparse.ArgumentParser(description='Парсер расписания samgtu')

    parser.add_argument('-df', '--date_from', type=str, help='Начальная дата в формате гггг-мм-дд')
    parser.add_argument('-dt', '--date_to', type=str, help='Конечная дата в формате гггг-мм-дд')
    parser.add_argument('-id', '--id', type=str, help='Просто передайте то, чему равен PHPSESSID')
    parser.add_argument('-a', '--auth', type=str, help='Введите логин и пароль: -a admin:password')

    args = parser.parse_args()

    if args.date_from:
        params['start'] = args.date_from + "T00:00:00+04:00"

    if args.date_to:
        params['end'] = args.date_to + "T00:00:00+04:00"

    if args.id:
        headers['Cookie'] = "PHPSESSID=" + args.id

    if args.auth:
        resp1 = requests.get(url_login)
        headers['Cookie'] = resp1.headers['Set-Cookie'].split(' ')[0]
        login = args.auth.split(':')[0]
        passwd = args.auth.split(':')[1]
        data = {
            '_csrf': 'qwerty==',
            'LoginForm[username]': login,
            'LoginForm[password]': passwd,
            'LoginForm[rememberMe]': 1
        }
        requests.post(url_login, headers=headers, data=data)

    parse_result = parse(params, headers)
    if parse_result:
        print(parse_result)


if __name__ == '__main__':
    main()
