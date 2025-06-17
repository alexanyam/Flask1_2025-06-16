from flask import Flask, request, jsonify
from random import choice
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.json.ensure_ascii = False

BASE_DIR = Path(__file__).parent
path_to_db = BASE_DIR / "store.db" # <- тут путь к БД

# quotes = [
#    {
#        "id": 3,
#        "author": "Rick Cook",
#        "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает.",
#        "rating": 2
#    },
#    {
#        "id": 5,
#        "author": "Waldi Ravens",
#        "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках.",
#        "rating": 1
#    },
#    {
#        "id": 6,
#        "author": "Mosher’s Law of Software Engineering",
#        "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили.",
#        "rating": 3
#    },
#    {
#        "id": 8,
#        "author": "Yoggi Berra",
#        "text": "В теории, теория и практика неразделимы. На практике это не так.",
#        "rating": 5
#    },
# ]



@app.route("/quotes")
def quotes_():
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    select_quotes = "SELECT * from quotes"
    cursor.execute(select_quotes)
    quotes_db = cursor.fetchall()
    cursor.close()
    connection.close()
    k = ("id", "author", "text")
    quotes = []
    for quote in quotes_db:
        quote = dict(zip(k, quote))
        quotes.append(quote)
    return jsonify(quotes_db), 200


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
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    insert_quotes = "INSERT INTO quotes (author,text) VALUES (?,?)"
    cursor.execute(insert_quotes, (data['author'], data['text']))
    print(cursor.rowcount, cursor.lastrowid)
    quotes_new_id = cursor.lastrowid
    cursor.close()
    connection.commit()
    connection.close()
    return jsonify(quotes_new_id), 200


@app.route("/quotes/<int:id>", methods=['PUT'])
def edit_quote(id):
    data = request.json
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    update_quotes = "UPDATE quotes SET text=? WHERE id=?"
    cursor.execute(update_quotes, (data['text'], id))
    quotes_new_id = cursor.lastrowid
    quotes_cr = cursor.rowcount
    cursor.close()
    connection.commit()
    connection.close()
    if quotes_cr:
        return jsonify(quotes_new_id, quotes_cr), 200
    else:    
       return {"error": f"Not found"}, 404


@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete(id):
    # data = request.json
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    delete_quotes = "DELETE FROM quotes WHERE id=?"
    cursor.execute(delete_quotes, [id])
    print(cursor.rowcount, cursor.lastrowid)
    quotes_new_id = cursor.lastrowid
    quotes_cr = cursor.rowcount
    cursor.close()
    connection.commit()
    connection.close()
    if quotes_cr:
        # return jsonify(quotes_new_id, quotes_cr), 200
       return f"Quote with id {id} is deleted.", 200
    else:    
    #    return {"error": f"Not found"}, 404
       return {"error": f"Quote with id={id} not found"}, 404

@app.route("/quotes/<int:id>")
def get_quote(id):
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    select_quotes = "SELECT * from quotes WHERE id=?"
    cursor.execute(select_quotes,[id])
    quotes_db = cursor.fetchall()
    cursor.close()
    connection.close()
    k = ("id", "author", "text")
    quotes = []
    for quote in quotes_db:
        quote = dict(zip(k, quote))
        quotes.append(quote)
    return jsonify(quotes_db), 200

@app.route("/quotes/count")
def count_():
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    select_quotes = "SELECT COUNT(*) from quotes"
    cursor.execute(select_quotes,)
    quotes_db = cursor.fetchone()
    cursor.close()
    connection.close()
    return jsonify(quotes_db), 200

@app.route("/quotes/random")
def round_():
   return jsonify(choice(quotes))

if __name__ == "__main__":
   app.run(debug=True)
