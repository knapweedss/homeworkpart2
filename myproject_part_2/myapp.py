# импортируем все необходимое
from flask import Flask
from flask import render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import sqlite3
import collections
from collections import Counter


db = sqlite3.connect('anketa.db')
cur = db.cursor()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///anketa.db'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    bilinguism = db.Column(db.Text)
    age = db.Column(db.Integer)
    gender = db.Column(db.Text)
    lives_now = db.Column(db.Text)
    origin = db.Column(db.Text)
    education = db.Column(db.Text)
    university = db.Column(db.Text)

class Questions(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)

class Answers(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True)
    q1 = db.Column(db.Text)
    q2 = db.Column(db.Text)
    q3 = db.Column(db.Text)
    q4 = db.Column(db.Text)
    q5 = db.Column(db.Text)


@app.route('/my_statistika.html')
def stats():

    age_info = {}  # статистика по возрасту
    age_stats = db.session.query(
        func.avg(User.age),  # средний возраст AVG(user.age)
        func.min(User.age),  # минимальный возраст MIN(user.age)
        func.max(User.age)  # максимальный возраст MAX(user.age)
    ).one()  # берем один результат 

    age_info['Средний возраст'] = age_stats[0]
    age_info['Минимальный возраст'] = age_stats[1]
    age_info['Максимальный возраст'] = age_stats[2]


# В каких городах живут сейчас люди, прошедшие опрос
    currently = db.session.query(User.lives_now).all()
    current_place = set(currently)

# ответы на вопросы
    all_answers = {}
    ans_q1 = Counter(db.session.query(Answers.q1)).most_common(3)
    ans_q2 = Counter(db.session.query(Answers.q2)).most_common(3)
    ans_q3 = Counter(db.session.query(Answers.q3)).most_common(3)
    ans_q4 = Counter(db.session.query(Answers.q4)).most_common(3)
    ans_q5 = Counter(db.session.query(Answers.q5)).most_common(3)

    all_answers['Вопрос 1'] = ans_q1
    all_answers['Вопрос 2'] = ans_q2
    all_answers['Вопрос 3'] = ans_q3
    all_answers['Вопрос 4'] = ans_q4
    all_answers['Вопрос 5'] = ans_q5

# Сколько людей из БГУ
    uni_bsu = db.session.query(User.university).filter_by(university='bsu')
    bsu = len(list(uni_bsu))


    return render_template('my_statistika.html', age_info=age_info,
            current_place=current_place, all_answers=all_answers, bsu=bsu)


@app.route('/')
def question_page():
    return render_template('my_opros.html')

@app.route('/my_opros.html')
def form():
    return redirect(url_for('question_page'))


@app.route('/process', methods=['get'])
def answer_process():

# проверка, что пользователь ответил на все вопросы
    if not request.args.get('gender') or not request.args.get('education') or not request.args.get('age') or \
            not request.args.get('lives_now') or not request.args.get('origin')or \
            not request.args.get('bilinguism') or not request.args.get('university'):
        return redirect(url_for('question_page'))
    else:
        gender = request.args.get('gender')  # запись в бд
        education = request.args.get('education')
        age = request.args.get('age')
        lives_now = request.args.get('lives_now')
        origin = request.args.get('origin')
        bilinguism = request.args.get('bilinguism')
        university = request.args.get('university')

        user = User(
            id=id(enumerate),
            age=age,
            gender=gender,
            education=education,
            lives_now=lives_now,
            origin=origin,
            bilinguism=bilinguism,
            university=university
        )
        db.session.add(user)
        db.session.commit()

        q1 = request.args.get('q1')
        q2 = request.args.get('q2')
        q3 = request.args.get('q3')
        q4 = request.args.get('q4')
        q5 = request.args.get('q5')
        answer = Answers(
            id = user.id + 1,
            q1=q1,
            q2=q2,
            q3=q3,
            q4=q4,
            q5=q5
            )
        db.session.add(answer)
        db.session.commit()
    return'Спасибо, это все, можете вернуться на главную страничку и перейти на страницу со статистикой!'

if __name__ == '__main__':
    app.run(debug=True)