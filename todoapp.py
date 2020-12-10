from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    author = db.Column(db.String(), nullable=False)
    thumbnail = db.Column(db.String(), nullable=True)
    page_count = db.Column(db.Integer, nullable=False)
    avg_rating = db.Column(db.Float, nullable=True)
    book_id = db.Column(db.Integer, nullable=False, unique=True)
    owner = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Book %r>' % self.id


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(300), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.id


@app.route('/save', methods=['POST'])
def save_book():
    id = request.args.get('id')
    data = ''
    save_error = 'Error saving data!'
    save_success = 'Added successfully!'
    if id:
        isbn = request.args.get('isbn')
        url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:{}'.format(isbn)
        try:
            response = requests.get(url)
            data = json.loads(response.text)
        except:
            return render_template('search.html', error=save_error)
    found_book = ''
    if data['items']:
        for book in data['items']:
            if book['id'] == id:
                found_book = book

    title = found_book['volumeInfo']['title']
    author = found_book['volumeInfo']['authors'][0]
    thumbnail = found_book['volumeInfo']['imageLinks']['smallThumbnail']
    page_count = found_book['volumeInfo']['pageCount']
    avg_rating = 0
    if 'averageRating' in found_book['volumeInfo']:
        avg_rating = found_book['volumeInfo']['averageRating']
    book_id = id
    new_book = Book(title=title, author=author, thumbnail=thumbnail, page_count=page_count, avg_rating=avg_rating,
                    book_id=book_id)
    try:
        db.session.add(new_book)
        db.session.commit()
        return render_template('booklists.html', success=save_success)
    except:
        return render_template('search.html', error=save_error)


@app.route('/', methods=['GET'])
def display_todo_list():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/search', methods=['GET'])
def search_page():
    return render_template('search.html')


@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')


@app.route('/post_user', methods=['POST'])
def post_user():
    email = request.form.get('email')
    password = request.form.get('password')
    new_todo = User(email=email, password=password)
    try:
        db.session.add(new_todo)
        db.session.commit()
        return redirect('/search')
    except:
        return redirect('/')


@app.route('/login_user/')
def login_user():
    login_message = ''
    email = request.args.get('email')
    password = request.args.get('password')
    user = User.query.filter_by(email=email).first()
    try:
        if user and user.password == password:
            res = Flask.make_response()
            res.set_cookie("owner", value=user['id'])
            return render_template('booklists.html')
        else:
            login_message = "Incorrect Login Credentials!"
    except:
        return render_template('login.html', login_message=login_message)


@app.route('/search_book/')
def search_book():
    search_message = 'Error getting data!'
    isbn = request.args.get('isbn')
    url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:{}'.format(isbn)
    try:
        response = requests.get(url)
        data = json.loads(response.text)
        count = data['totalItems']
        return render_template('search.html', isbn=isbn, count=count, books=data['items'])
    except:
        return render_template('search.html', error=search_message)


#
# @app.route('/delete/<int:id>')
# def delete(id):
#     todo_to_delete = Todo.query.get_or_404(id)
#
#     try:
#         db.session.delete(todo_to_delete)
#         db.session.commit()
#         return redirect('/')
#     except:
#         return redirect('/')
#
#
# @app.route('/clear')
# def clear():
#     todos = Todo.query.all()
#     try:
#         for todo in todos:
#             todo_to_delete = Todo.query.get_or_404(todo.id)
#             db.session.delete(todo_to_delete)
#         db.session.commit()
#         return redirect('/')
#     except:
#         return redirect('/')
#

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, use_reloader=True)
