import os

from flask import Flask, render_template, request, redirect
from flask_migrate import Migrate
from dbmodels import *
from forms import RequestForm, BookingForm


goals = {"travel": "⛱ Для путешествий", "study": "🏫 Для учебы", "work": "🏢 Для работы", "relocate": "🚜 Для переезда", "coding": "🙈 Для кодинга"}
week_days = {"mon": "Понедельник", "tue": "Вторник", "wed": "Среда", "thu": "Четверг", "fri": "Пятница", "sat": "Суббота", "sun": "Воскресенье"}

app = Flask(__name__)
app.secret_key = "4iko42k24pk"

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)


@app.errorhandler(404)
def render_not_found(error): return "Ничего не нашлось! Вот неудача, отправляйтесь на главную!"


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


if __name__ == '__main__':
    app.run()
