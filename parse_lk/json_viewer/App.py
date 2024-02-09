from flask import Flask, render_template
import os
import json

app = Flask(__name__)
JSON_FOLDER = '../json/'

@app.route('/')
def index():
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
