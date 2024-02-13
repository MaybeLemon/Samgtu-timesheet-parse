from flask import Flask, render_template, request
import os
import json
from getter import Getter
from scripts import *


app = Flask(__name__)
JSON_FOLDER = '../json/'

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')

@app.route('/', methods=['GET', 'POST'])
def generate():
    if request.method == 'GET':
        return render_template('generate_json.html')
    elif request.method == 'POST':
        getter = Getter()
        if 'btn1' in request.form:
            login = request.form['login']
            passwd = request.form['passwd']
            getter.authorize(login, passwd)
            new_data = getter.parse()
            if new_data != 0:
                return render_template('generate_json.html', otvet='Парсинг прошёл успешно')
            else:
                return render_template('generate_json.html', otvet='Ошибка при парсинге')
        elif 'btn2' in request.form:
            sessid = request.form['sessid']
            getter.cookie(sessid)
            new_data = getter.parse()
            if new_data != 0:
                return render_template('generate_json.html', otvet='Парсинг прошёл успешно')
            else:
                return render_template('generate_json.html', otvet='Ошибка при парсинге')



@app.route('/viewer')
def view():
    json_files = [f for f in os.listdir(JSON_FOLDER) if f.endswith('.json')]
    numbers = [f.split('_')[1].split('.')[0] for f in json_files]
    return render_template('json_select.html', numbers=numbers)

@app.route('/<int:number>', methods=['GET', 'POST'])
def json_page(number):
    data = {}
    json_file = f'data_{number}.json'
    if os.path.exists(os.path.join(JSON_FOLDER, json_file)):
        with open(os.path.join(JSON_FOLDER, json_file), 'r', encoding='utf-8') as f:
            lessons = json.load(f)

        data['unique_names'] = give_unique_names(lessons)
        data['unique_teacher'] = give_unique_teachers(lessons)
        data['lessons'] = lessons
        if request.method == 'GET':
            return render_template('timesheet.html', data=data)
        elif request.method == 'POST':
            if 'sort' in request.form:
                date = request.form['date']
                sub_type = request.form['sub_type']
                data = sort_btn(data, date, sub_type, lessons)
                return render_template('timesheet.html', data=data)

            elif 'sub_info' in request.form:
                sub = request.form['sub_type']
                data = sub_info_btn(data, sub, lessons)
                return render_template('timesheet.html', data=data)

            elif 'teacher_sub' in request.form:
                teacher = request.form['teacher_info']
                data = teacher_sub_btn(data, teacher, lessons)
                return render_template('timesheet.html', data=data)

            else:
                return render_template('timesheet.html', data=data)
    else:
        return render_template('404.html')





if __name__ == '__main__':
    app.run(debug=True)
