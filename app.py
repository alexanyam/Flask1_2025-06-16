from flask import Flask, request, jsonify, g
from random import choice
import sqlite3
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, func, insert, update
from sqlalchemy.exc import InvalidRequestError
from flask_migrate import Migrate


class Base(DeclarativeBase):
    pass

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.json.ensure_ascii = False

db_file = 'quotes.db'
path_to_db = BASE_DIR / db_file  # <- тут путь к БД
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(model_class=Base)
db.init_app(app)
migrate = Migrate(app, db)

class QuoteModel(db.Model):
    __tablename__ = 'quotes'
    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(32))
    text: Mapped[str] = mapped_column(String(255))
    rating: Mapped[int]
    def __init__(self, author, text, rating):
        self.author = author
        self.text = text
        self.rating = rating

    def to_dict(self):
        return{"id": self.id, "author": self.author, "text": self.text, "rating": self.rating}

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(path_to_db)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def new_table(name_db:str):
    import sqlite3
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()

    create_table = f"""
    CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT NOT NULL,
    text TEXT NOT NULL,
    rating INT NOT NULL
    );
    """
    cursor.execute(create_table)
    connection.commit()

    # create_quotes = f"""
    # INSERT INTO
    # quotes (author, text, rating)
    # VALUES
    # ('Rick Cook', 'Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает.',4),
    # ('Waldi Ravens', 'Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках.', 1),
    # ('Mosher’s Law of Software Engineering', 'Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили.',2),
    # ('Yoggi Berra', 'В теории, теория и практика неразделимы. На практике это не так.',5);
    # """
    # cursor.execute(create_quotes)
    # connection.commit()
    cursor.close()
    connection.close()
    return(200)

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
def get_quotes():
    #-> list[dict[str, Any]]:
    quotes_db = db.session.scalars(db.select(QuoteModel)).all()
    quotes = []
    for quote in quotes_db:
            quotes.append(quote.to_dict())
    return jsonify(quotes), 200

@app.route("/quotes/<int:id>")
def get_quote(id):
    quotes_db = db.session.scalars(db.select(QuoteModel).filter_by(id=id)).all()
    quotes = []
    for quote in quotes_db:
            quotes.append(quote.to_dict())
    return jsonify(quotes), 200

@app.route("/quotes/count")
def count_():
    count = db.session.scalar(func.count(QuoteModel.id))
    return jsonify(count = count), 200


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

    stmt = insert(user_table).values(name="username", fullname="Full Username")

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
    attributes: set = set(data.keys()) & {'author','rating','text'}
    if "rating" in attributes and data["rating"] not in range(1,6):
        attributes.remove("rating")
    if attributes:
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()
        update_quotes = f"UPDATE quotes SET {', '.join(attr+'=?' for attr in attributes)} WHERE id=?"
        params = tuple(data.get(attr) for attr in attributes) + (id,)
        cursor.execute(update_quotes, params)
        quotes_new_id = cursor.lastrowid
        quotes_cr = cursor.rowcount
        cursor.close()
        connection.commit()
        connection.close()
        if quotes_cr:
            return jsonify(quotes_new_id, quotes_cr), 200
        else:
           return {"error": f"Record not updated"}, 404
    else:
       return {"error": f"No data"}, 404

@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete(id):
    # data = request.json
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    delete_quotes = "DELETE FROM quotes WHERE id=?"
    cursor.execute(delete_quotes, [id])
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

# @app.route("/quotes/count")
# def count_():
#     connection = sqlite3.connect(path_to_db)
#     cursor = connection.cursor()
#     select_quotes = "SELECT COUNT(*) from quotes"
#     quotes_db = cursor.execute(select_quotes).fetchone()
#     cursor.close()
#     connection.close()
#     return jsonify({"count":quotes_db[0]}), 200

@app.route("/quotes/random")
def round_():
    cursor = get_db().cursor()
    select_quotes = "SELECT * from quotes"
    cursor.execute(select_quotes)
    quotes_db = choice(cursor.fetchall())
    k = ("id", "author", "text", "rating")
    quotes = []
    for quote in quotes_db:
        quote = dict(zip(k, quotes_db))
        quotes.append(quote)
    # return jsonify(quotes), 200
    # print(choice(quotes))
    return jsonify(choice(quotes)), 200

if __name__ == "__main__":
    new_table('quotes')
    app.run(debug=True)
