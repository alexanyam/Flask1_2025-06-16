from flask import Flask, request, jsonify
from random import choice
import sqlite3

app = Flask(__name__)
app.json.ensure_ascii = False

quotes = [
   {
       "id": 3,
       "author": "Rick Cook",
       "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает.",
       "rating": 2
   },
   {
       "id": 5,
       "author": "Waldi Ravens",
       "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках.",
       "rating": 1
   },
   {
       "id": 6,
       "author": "Mosher’s Law of Software Engineering",
       "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили.",
       "rating": 3
   },
   {
       "id": 8,
       "author": "Yoggi Berra",
       "text": "В теории, теория и практика неразделимы. На практике это не так.",
       "rating": 5
   },
]

@app.route("/")
def hello_world():
   return "Hello, World!"

about_me = {
   "name": "Александр",
   "surname": "Морозов",
   "email": "am@mail.ru"
}

@app.route("/about")
def about():
   return about_me

# @app.route("/quotes")
# def quotes_():
#    return quotes

@app.route("/quotes")
def quotes_():
    connection = sqlite3.connect("store.db")
    # Создаем cursor, он позволяет делать SQL-запросы
    cursor = connection.cursor()
    select_quotes = "SELECT * from quotes"
    cursor.execute(select_quotes)
    # Извлекаем результаты запроса
    quotes = cursor.fetchall()
    # Закрыть курсор:
    cursor.close()
    # Закрыть соединение:
    connection.close()
#    print(f"{quotes=}")
    return quotes


@app.route("/quotes/filter")
def quotes_filt():
    quotes_f = quotes.copy()
    for k, v in request.args.items():
        if k not in ("author", "rating"):
            return f"Not Key {k}", 400
        if k == "rating":
            v = int(v)
        quotes_f = [i for i in quotes_f if i[k] == v]
    return quotes_f

@app.route("/quotes", methods=['POST'])
def create_quote():
    data = request.json
    last_quote = quotes[-1]
    new_id = last_quote["id"] + 1
    data["id"] = new_id
    rating = data.get("rating")
    if rating is None or rating not in range(1,6):
        data["rating"] = 1
    quotes.append(data)
    return data, 201

@app.route("/quotes/<int:id>", methods=['PUT'])
def edit_quote(id):
    new_data = request.json
    if not set(new_data.keys()) - set(('author', 'rating', 'text')):
        for i in quotes:
            if i["id"] == id:
                if "rating" in new_data and new_data["rating"] not in range(1, 6):
                    new_data.pop("rating")
                i.update(new_data)
    else:
        return {"error"}, 404
    return {"error": f"Not found"}, 404

    # last_quote = quotes[-1]
    # new_id = last_quote["id"] + 1
    # new_data["id"] = new_id
    # quotes.append(new_data)
    # return new_data, 201

@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete(id):
    for i in quotes:
        if i["id"] == id:
            quotes.remove(i)
            return f"Quote with id {id} is deleted.", 200
    return {"error": f"Quote with id={id} not found"}, 404

@app.route("/quotes/<int:id>")
def get_quote(id):
    for i in quotes:
        if i["id"] == id:
            return i, 200
    return f"Quote with id={id} not found", 404

@app.route("/quotes/count")
def count_():
   return jsonify(str(len(quotes)))

@app.route("/quotes/random")
def round_():
   return jsonify(choice(quotes))

if __name__ == "__main__":
   app.run(debug=True)
