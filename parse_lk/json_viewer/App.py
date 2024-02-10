from flask import Flask, render_template, request
import os
import json
from getter import Getter

app = Flask(__name__)
JSON_FOLDER = '../json/'

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')

@app.route('/', methods=['GET', 'POST'])
def generate():
    getter = Getter()
    if request.method == 'POST':
        if 'btn1' in request.form:
            login = request.form['login']
            passwd = request.form['passwd']
            getter.authorize(login, passwd)
            new_data = getter.parse()
            if new_data != 0:
                return render_template('generate.html', otvet='Парсинг прошёл успешно')
            else:
                return render_template('generate.html', otvet='Ошибка при парсинге')
        elif 'btn2' in request.form:
            sessid = request.form['sessid']
            getter.cookie(sessid)
            new_data = getter.parse()
            if new_data != 0:
                return render_template('generate.html', otvet='Парсинг прошёл успешно')
            else:
                return render_template('generate.html', otvet='Ошибка при парсинге')

    return render_template('generate.html')


@app.route('/viewer')
def view():
    json_files = [f for f in os.listdir(JSON_FOLDER) if f.endswith('.json')]
    numbers = [f.split('_')[1].split('.')[0] for f in json_files]
    return render_template('index.html', numbers=numbers)

@app.route('/<int:number>')
def json_page(number):
    json_file = f'data_{number}.json'
    if os.path.exists(os.path.join(JSON_FOLDER, json_file)):
        with open(os.path.join(JSON_FOLDER, json_file), 'r', encoding='utf-8') as f:
            lessons = json.load(f)
        return render_template('rasp.html', lessons=lessons)
    else:
        return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True)
