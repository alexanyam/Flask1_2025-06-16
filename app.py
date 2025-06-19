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
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


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

class AuthorModel(db.Model):
    __tablename__ = 'authors'
    id: Mapped[int] = mapped_column(primary_key=True)
    surname: Mapped[int] = mapped_column(String(32), index= True, default = '', server_default = '')
    name: Mapped[int] = mapped_column(String(32))
    quotes: Mapped[list['QuoteModel']] = relationship( back_populates='author', lazy='dynamic')
    def __init__(self, id, surname, name):
        self.id = id
        self.surname = surname
        self.name = name

    def to_dict(self):
        return{"id": self.id, "surname": self.surname, "name": self.name}    

class QuoteModel(db.Model):
    __tablename__ = 'quotes'
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[str] = mapped_column(ForeignKey('authors.id'))
    author: Mapped['AuthorModel'] = relationship(back_populates='quotes')
    text: Mapped[str] = mapped_column(String(255))
    rating: Mapped[int]=mapped_column(default = '1', server_default = '1')
    def __init__(self, author, text, rating):
        self.author = author
        # self.author_id = author_id
        self.text = text
        self.rating = rating

    def to_dict(self):
        return{"id": self.id, "text": self.text, "rating": self.rating, "author": self.author}       

# class QuoteModel(db.Model):
#     __tablename__ = 'quotes'
#     id: Mapped[int] = mapped_column(primary_key=True)
#     author: Mapped[str] = mapped_column(String(32))
#     text: Mapped[str] = mapped_column(String(255))
#     rating: Mapped[int]
#     def __init__(self, author, text, rating):
#         self.author = author
#         self.text = text
#         self.rating = rating


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

# Список всех авторов
@app.route("/authors")
def get_authors():
    #-> list[dict[str, Any]]:
    quotes_db = db.session.scalars(db.select(AuthorModel)).all()
    # quotes_db = db.session.scalars(db.select(AuthorModel)).all()
    # quotes_db = db.session.get(AuthorModel,)
    quotes = []
    for quote in quotes_db:
            quotes.append(quote.to_dict())
    return jsonify(quotes), 200

# # Цитаты по id автора
# @app.route("/authors/<int:id>/quotes")
# def get_authors_quotes(id): 
# # -> list[dict[str, Any]]:
#     quotes_db = db.session.get(AuthorModel, id)
#     if quotes_db:
#         quotes = []
#         for quote in quotes_db.quotes:
#                 quotes.append(quote.to_dict())
#         return jsonify(quotes), 200
#     else:
#         return {"Error":f"Не найдены цитаты с id автора = {id}"}, 400  

# Автор по id
@app.route("/authors/<int:id>")
def get_author(id): 
# -> list[dict[str, Any]]:
    quotes_db = db.session.get(AuthorModel, id)
    # quotes = []
    # for quote in quotes_db.name:
    #         quotes.append(quote.to_dict())
    if quotes_db:
        return jsonify(quotes_db.name+' '+quotes_db.surname), 200  
    else:
        return {"Error":f"Не найден id автора = {id}"}, 400       

# Создать автора
@app.route("/authors", methods=['POST'])
def create_author():
    data = request.json
    author1 = AuthorModel(id=None, name=data['name'], surname=data['surname'])
    db.session.add(author1)
    db.session.commit()
    return {"Result":f"Добавлен автор: {data['name']+' '+ data['surname']}"}, 200 

# Редактировать автора по id
@app.route("/authors/<int:id>", methods=['PUT'])
def edit_author(id):
    data = request.json
    author1 = db.session.get(AuthorModel, id)
    if author1:
        author1.name = data['name']
        author1.surname = data['surname']
        db.session.commit()
        return {"Result:":f"Изменен автор с id = {id} на {data['name']+' '+data['surname']}"}, 200  
    else:
        return {"Error":f"Не найден id автора = {id}"}, 400  

# Удалить автора
@app.route("/authors/<int:au_id>", methods=['DELETE'])
def delete_author(au_id):
    quotes_db = db.session.get(AuthorModel, au_id)
    if quotes_db:
        db.session.delete(quotes_db)
        db.session.commit()
        return {"Result":f"Удален автор с id = {au_id}"}, 200  
    else:
        return {"Error":f"Не найден id автора = {au_id}"}, 400    

###################################################################################
# Цитаты
@app.route("/quotes")
def get_quotes():
    quotes_db = db.session.scalars(db.select(QuoteModel.text)).all()
    return jsonify(quotes_db), 200 

# Цитата по id
@app.route("/quotes/<int:id>")
def get_quote(id): 
    quotes_db = db.session.get(QuoteModel, id)
    if quotes_db:
        return {"text": quotes_db.text}, 200  
        # return jsonify(quotes.to_dict()), 200    
        # return quotes_db.text, 200    
    else:
        return {"Error":f"Не найден id цитаты = {id}"}, 400   

# Цитаты по id автора
@app.route("/authors/<int:id>/quotes")
def get_authors_quotes(id): 
# -> list[dict[str, Any]]:
    au = db.session.get(AuthorModel, id)
    print(au.name)
    if au:
        q_db = db.session.query(QuoteModel).with_entities(QuoteModel.id,QuoteModel.text).filter(QuoteModel.author_id == id).all()
        return jsonify(dict(q_db)), 200 
    else:
        return {"Error":f"Не найдены цитаты с id автора = {id}"}, 400  
  

# Создать цитату 
@app.route("/authors/<int:id>/quotes", methods=['POST'])
def create_quote(id):
    data = request.json
    au_db = db.session.get(AuthorModel, id)
    if data['rating']>0 & data['rating']<6:
        r = data['rating']
    else:
        r=1
    q1 = QuoteModel(text=data['text'], rating=r, author = au_db)
    db.session.add(q1)
    db.session.commit()
    return {"Result":f"Добавлена цитата: {data['text']}"}, 200 

# Редактировать цитату по id
@app.route("/quotes/<int:id>", methods=['PUT'])
def edit_quote(id):
    data = request.json
    q1 = db.session.get(QuoteModel, id)
    if q1:
        q1.text = data['text']
        if int(data['rating'])>0 and int(data['rating'])<6:
            q1.rating = str(data['rating'])
        else:
            q1.rating = '1'
        db.session.commit()
        return {"Result:":f"Изменена цитата с id = {id} на {data['text']}"}, 200  
    else:
        return {"Error":f"Не найден id цитаты = {id}"}, 400  

# Удалить цитату
@app.route("/quotes/<int:q_id>", methods=['DELETE'])
def delete_quotes(q_id):
    quotes_db = db.session.get(QuoteModel, q_id)
    if quotes_db:
        db.session.delete(quotes_db)
        db.session.commit()
        return {"Result":f"Удалена цитата с id = {q_id}"}, 200  
    else:
        return {"Error":f"Не найден id цитаты = {q_id}"}, 400  

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

@app.route("/authors/<int:id>/quotes", methods=['POST'])
def create_quote_au():
    data = request.json
    author1 = AuthorModel(name=data['name'])
    db.session.add(author1)
    db.session.commit()
    q1 = QuoteModel(author1, data['text'])
    db.session.add(q1)
    db.session.commit()
    return "OK", 200


# @app.route("/quotes/<int:id>", methods=['DELETE'])
# def delete(id):
#     # data = request.json
#     connection = sqlite3.connect(path_to_db)
#     cursor = connection.cursor()
#     delete_quotes = "DELETE FROM quotes WHERE id=?"
#     cursor.execute(delete_quotes, [id])
#     quotes_new_id = cursor.lastrowid
#     quotes_cr = cursor.rowcount
#     cursor.close()
#     connection.commit()
#     connection.close()
#     if quotes_cr:
#         # return jsonify(quotes_new_id, quotes_cr), 200
#        return f"Quote with id {id} is deleted.", 200
#     else:    
#     #    return {"error": f"Not found"}, 404
#        return {"error": f"Quote with id={id} not found"}, 404

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
