from os import path
import json
from data import teachers


if not path.exists("data.json"):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(teachers, f, ensure_ascii=False)
        print('Saved to json')