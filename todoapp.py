from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.db'
db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    author = db.Column(db.String(), nullable=False)
    thumbnail = db.Column(db.String(), nullable=False)
    page_count = db.Column(db.Integer, nullable=False)
    avg_rating = db.Column(db.Float, nullable=False)
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


@app.route('/', methods=['GET'])
def display_todo_list():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/search', methods=['GET'])
def index():
    return render_template('search.html')


@app.route('/post_user', methods=['POST'])
def post_user():
    email = request.form.get('email')
    password = request.form.get('password')
    new_todo = User(email=email, password=password)
    try:
        db.session.add(new_todo)
        db.session.commit()
        return redirect('/')
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
            return render_template('/booklists.html')
        else:
            login_message = "Incorrect Login Credentials!"
    except:
        return render_template('login.html', login_message=login_message)


@app.route('/search_book/')
def search_book():
    search_message = ''
    isbn = request.args.get('isbn')
    url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:{}'.format(isbn)
    try:
        response = requests.get(url)
        return render_template('search.html', books=response.json())
    except:
        return render_template('search.html')


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
    app.run(debug=True)
