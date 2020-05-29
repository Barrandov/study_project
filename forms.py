from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, HiddenField
from wtforms.validators import InputRequired, Length


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

