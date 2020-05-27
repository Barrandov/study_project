import json
import random

from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, HiddenField
from wtforms.validators import InputRequired, Length
from flask_sqlalchemy import SQLAlchemy

from data import goals, week_days

app = Flask(__name__)
app.secret_key = "4iko42k24pk"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///stepik.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.errorhandler(404)
def render_not_found(error): return "Ничего не нашлось! Вот неудача, отправляйтесь на главную!"


teacher_goals_association = db.Table(
    'teacher_goals',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.ID')),
    db.Column('goal_id', db.Integer, db.ForeignKey('goals.ID')),
)


class Teachers(db.Model):
    __tablename__ = 'teachers'
    id = db.Column('ID', db.Integer, primary_key=True)
    name = db.Column('Name', db.String)
    about = db.Column('About', db.String)
    rating = db.Column('Rating', db.Float)
    picture = db.Column('Picture', db.String)
    price = db.Column('Price', db.Integer)
    schedule = db.relationship('Schedule', backref='teacher')
    goals = db.relationship('Goals', secondary=teacher_goals_association, backref='teacher')
    booking = db.relationship('Booking', backref='teacher')


class Goals(db.Model):
    __tablename__ = 'goals'
    id = db.Column('ID', db.Integer, primary_key=True)
    goal_slug = db.Column('Goal slug', db.String)
    goal_text = db.Column('Goal text', db.String)


class Schedule(db.Model):
    __tablename__ = 'schedule'
    id = db.Column('ID', db.Integer, primary_key=True)
    week_day = db.Column('Week Day', db.String)
    timing = db.Column('Timing', db.String)
    teacher_id = db.Column('Teacher ID', db.Integer, db.ForeignKey('teachers.ID', ondelete='CASCADE'))


class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column('ID', db.Integer, primary_key=True)
    name = db.Column('Name', db.String)
    phone = db.Column('Phone', db.String)
    week_day = db.Column('Week Day', db.String)
    timing = db.Column('Timing', db.String)
    teacher_id = db.Column('Teacher ID', db.Integer, db.ForeignKey('teachers.ID', ondelete='CASCADE'))


class RequestLesson(db.Model):
    id = db.Column('ID', db.Integer, primary_key=True)
    name = db.Column('Name', db.String)
    phone = db.Column('Phone', db.String)
    goal = db.Column('Goal', db.String)
    timing = db.Column('Timing', db.String)


def convert():
    for k, v in goals.items():
        goal_add = Goals(goal_slug=k, goal_text=v)
        db.session.add(goal_add)

    with open('data.json', 'r') as zapis:
        all_data = json.load(zapis)

    for data in all_data:
        print(data['name'])
        teacher_add = Teachers(name=data['name'],
                               about=data['about'],
                               rating=data['rating'],
                               picture=data['picture'],
                               price=data['price']
                               )

        db.session.add(teacher_add)

        for week, result in data['free'].items():
            for k, v in result.items():
                if v:
                    sh_add = Schedule(week_day=week, timing=k, teacher=teacher_add)
                    db.session.add(sh_add)
    else:
        db.create_all()
        db.session.commit()

        for data in all_data:

            t = db.session.query(Teachers).filter(Teachers.name == data['name']).first()
            for i in data['goals']:
                get_slug = db.session.query(Goals).filter(Goals.goal_slug == i).first()
                t.goals.append(get_slug)

        db.session.commit()


# convert()


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
    teachers = db.session.query(Teachers).order_by(db.func.random()).limit(6)
    return render_template('index.html', teachers=teachers[:6], goals=goals)


@app.route('/all/')
def all_render():
    teachers = db.session.query(Teachers).all()
    return render_template('index.html', teachers=teachers, goals=goals)


@app.route('/goals/<goal>/')
def goals_render(goal):
    teachers_with_goals = db.session.query(Teachers).filter(Teachers.goals.any(goal_slug=goal)).all()
    return render_template('goal.html', goal_label=goals[goal], teachers=teachers_with_goals, goals=goals)


@app.route('/profile/<int:id>')
def profiles_render(id):
    teacher_slots = db.session.query(Schedule).filter(Schedule.teacher_id == id).all()
    slots = {'mon': [], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': []}

    teacher_id = db.session.query(Teachers).get_or_404(id)

    for i in teacher_slots:
        slots[i.week_day].append(i.timing)

    return render_template('profile.html',
                           teacher=teacher_id,
                           teacher_slots=slots,
                           goals=goals,
                           week_days=week_days)


@app.route('/request/', methods=['GET', 'POST'])
def request_render():
    form = RequestForm()

    if request.method == 'POST':
        request_data = {'name': form.name.data,
                        'phone': form.phone.data,
                        'goal': form.goals.data,
                        'timing': form.timing.data
                        }

        request_db = RequestLesson(name=request_data['name'],
                                   phone=request_data['phone'],
                                   goal=request_data['goal'],
                                   timing=request_data['timing']
                                   )

        db.session.add(request_db)
        db.session.commit()

        return render_template('request_done.html', request_data=request_data, goals=goals)

    return render_template('request.html', form=form)


@app.route('/booking/<int:id>/<day>/<time>/', methods=["POST", "GET"])
def booking_render(id, day, time):
    if request.method == "POST":

        form = BookingForm()

        booking_data = {'name': form.name.data,
                        'phone': form.phone.data,
                        'teacher_id': form.teacher_id.data,
                        'day': form.day_hide.data,
                        'timing': form.timing_hide.data
                        }
        check_user = db.session.query(Booking).filter(Booking.name == booking_data['name'],
                                                      Booking.phone == booking_data['phone'],
                                                      Booking.teacher_id == booking_data['teacher_id'],
                                                      Booking.week_day == booking_data['day'],
                                                      Booking.timing == booking_data['timing']).first()

        if check_user:
            return 'Повторный запрос в БД!'

        teacher_time_delete = db.session.query(Schedule) \
            .filter(Schedule.teacher_id == booking_data['teacher_id']). \
            filter(Schedule.week_day == booking_data['day']). \
            filter(Schedule.timing == booking_data['timing'].replace('-', ':')). \
            first()

        booking_add = Booking(name=booking_data['name'],
                              phone=booking_data['phone'],
                              week_day=booking_data['day'],
                              timing=booking_data['timing'],
                              teacher_id=booking_data['teacher_id']
                              )

        db.session.delete(teacher_time_delete)
        db.session.add(booking_add)
        db.session.commit()

        return render_template('booking_done.html', booking_data=booking_data, week_days=week_days)
    # else
    teacher_is_free = db.session.query(Schedule) \
        .filter(Schedule.teacher_id == id). \
        filter(Schedule.week_day == day). \
        filter(Schedule.timing == time.replace('-', ':')). \
        first()

    teacher_id = db.session.query(Teachers).get(id)

    if teacher_is_free:
        form = BookingForm()
        return render_template('booking.html',
                               teacher=teacher_id,
                               form=form,
                               day=day,
                               week_days=week_days,
                               time=time.replace('-', ':'))

    else:
        return "В этом слоте занято"


@app.route('/list/')
def list_render():
    booking = db.session.query(Booking).all()
    booking_list = []
    for i in booking:
        booking_list.append((i.id, i.name, i.phone, week_days[i.week_day], i.timing, i.teacher.name))
    return render_template('list.html', goals=goals, books=booking_list)


@app.route('/list/delete/<int:id>/')
def list_delete_render(id):
    booking = db.session.query(Booking).filter(Booking.id == id).first()
    back_time = Schedule(week_day=booking.week_day, timing=booking.timing, teacher_id=booking.teacher_id)
    db.session.add(back_time)
    db.session.delete(booking)
    db.session.commit()
    return redirect('/list/')


app.run('0.0.0.0', debug=False)
