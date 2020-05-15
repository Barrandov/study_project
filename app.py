import json
import random
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, HiddenField
from wtforms.validators import InputRequired, Length
from data import goals, week_days

app = Flask(__name__)
app.secret_key = "4iko42k24pk"


def open_json(file):
    with open(file, 'r') as json_file:
        return json.load(json_file)


def write_json(data, file):
    with open(file, 'w', encoding='utf8') as json_file:
        json.dump(data, json_file, ensure_ascii=False)


class RequestForm(FlaskForm):
    name = StringField('Вас зовут', [InputRequired()])
    phone = StringField('Ваш телефон', [Length(min=5)])
    goals = RadioField('goals', choices=[("travel", "⛱ Для путешествий"),
                                         ("study", "🏫 Для учебы"),
                                         ("work", "🏢 Для работы"),
                                         ("relocate", "🚜 Для переезда"),
                                         ("coding", "🙈 Для кодинга")],
                       default="travel")

    timing = RadioField('timing', choices=[("1-2", "1 - 2 часа в неделю"),
                                           ("3-5", "3-5 часов в неделю"),
                                           ("5-7", "5-7 часов в неделю"),
                                           ("7-10", "7-10 часов в неделю")],
                        default="1-2")


class BookingForm(RequestForm):
    teacher_id = HiddenField('teacher_id')
    day_hide = HiddenField('day')
    timing_hide = HiddenField('timing')


@app.route('/')
def index_render():
    teachers = open_json('data.json')
    random.shuffle(teachers)
    return render_template('index.html', teachers=teachers[:6], goals=goals)


@app.route('/all/')
def all_render():
    teachers = open_json('data.json')
    return render_template('index.html', teachers=teachers, goals=goals)


@app.route('/goals/<goal>/')
def goals_render(goal):
    teachers = open_json('data.json')
    teachers_with_goals = [i for i in teachers if goal in i['goals']]
    return render_template('goal.html', goal_label=goals[goal], teachers=teachers_with_goals, goals=goals)


@app.route('/profile/<int:id>')
def profiles_render(id):
    teachers = open_json('data.json')
    teacher_with_id = [i for i in teachers if i['id'] == id]
    teacher_slots = teacher_with_id[0]['free']
    return render_template('profile.html',
                           teacher=teacher_with_id,
                           teacher_slots=teacher_slots,
                           goals=goals,
                           week_days=week_days)


@app.route('/request/')
def request_render():
    form = RequestForm()
    return render_template('request.html', form=form)


@app.route('/request_done/', methods=['GET', 'POST'])
def request_done_render():
    if request.method == 'POST':
        form = RequestForm()

        data = open_json('request.json')
        request_data = {'id': len(data),
                        'name': form.name.data,
                        'phone': form.phone.data,
                        'goal': form.goals.data,
                        'timing': form.timing.data
                        }
        data.append(request_data)
        write_json(data, 'request.json')

        return render_template('request_done.html', request_data=request_data, goals=goals)
    else:
        return "Просто зашли посмотреть"


@app.route('/booking/<int:id>/<day>/<time>/')
def booking_render(id, day, time):
    teacher = open_json('data.json')[id]

    if teacher['free'][day][time.replace('-', ':')]:
        form = BookingForm()
        return render_template('booking.html',
                               teacher=teacher,
                               form=form,
                               day=day,
                               week_days=week_days,
                               time=time.replace('-', ':'))

    else:
        return "В этом слоте занято"


@app.route('/booking_done/', methods=["POST", "GET"])
def booking_done_render():
    if request.method == "POST":
        form = BookingForm()

        booking_json = open_json('booking.json')
        request_json = open_json('data.json')

        booking_data = {'id': len(booking_json),
                        'name': form.name.data,
                        'phone': form.phone.data,
                        'teacher_id': form.teacher_id.data,
                        'day': form.day_hide.data,
                        'timing': form.timing_hide.data
                        }

        booking_json.append(booking_data)

        for i in request_json:
            if i['id'] == int(booking_data['teacher_id']):
                i['free'][booking_data['day']][booking_data['timing']] = False

        write_json(request_json, 'data.json')
        write_json(booking_json, 'booking.json')

        return render_template('booking_done.html', booking_data=booking_data, week_days=week_days)

    return "Нет тут ничего"


app.run('0.0.0.0', debug=True)
