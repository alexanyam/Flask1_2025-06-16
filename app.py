from flask import Flask
from flask import request
from random import choice

app = Flask(__name__)
app.json.ensure_ascii = False

@app.route("/")
def hello_world():
   return "Hello, World!"

about_me = {
   "name": "Вадим",
   "surname": "Шиховцов",
   "email": "vshihovcov@specialist.ru"
}

@app.route("/about")
def about():
   return about_me

quotes = [
   {
       "id": 3,
       "author": "Rick Cook",
       "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает."
   },
   {
       "id": 5,
       "author": "Waldi Ravens",
       "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках."
   },
   {
       "id": 6,
       "author": "Mosher’s Law of Software Engineering",
       "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили."
   },
   {
       "id": 8,
       "author": "Yoggi Berra",
       "text": "В теории, теория и практика неразделимы. На практике это не так."
   },
]

# @app.route("/quotes")
# def quotes_():
#    return quotes

@app.route("/quotes", methods=['POST'])
def create_quote():
   data = request.json
   print("data = ", data)
   return {}, 201

@app.route("/quotes/<int:id>")
def get_quote(id):
    # if quotes.get("id", id) != None:
    return quotes[id]
    # else:
    #     return f"Quote with id={id} not found", 404   

@app.route("/quotes/count")
def count_():
   return str(len(quotes))

@app.route("/quotes/random")
def round_():
   return choice(quotes)

if __name__ == "__main__":
   app.run(debug=True)
