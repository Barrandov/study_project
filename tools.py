import json

from dbmodels import *

goals = {"travel": "⛱ Для путешествий", "study": "🏫 Для учебы", "work": "🏢 Для работы", "relocate": "🚜 Для переезда", "coding": "🙈 Для кодинга"}

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


convert()
