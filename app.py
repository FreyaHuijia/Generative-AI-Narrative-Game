from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv()

app =Flask(__name__, template_folder = 'templates', static_folder='static',static_url_path='/')

@app.route('/')
def index():
    return render_template('about.html')

@app.route('/milestone1')
def interaction_1():
    return render_template('milestone1.html', active='interaction_1')


if __name__ == '__main__':
    app.run(host='0.0.0.0')