from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
