from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Todo %r>' % self.id


@app.route('/', methods=['GET'])
def display_todo_list():
    todos = Todo.query.order_by(Todo.timestamp).all()
    return render_template('index.html', todos=todos)


@app.route('/submit', methods=['POST'])
def add_todo():
    title = request.form.get('task')
    email = request.form.get('email')
    priority = request.form.get('priority')
    new_todo = Todo(text=title, email=email, priority=priority)
    try:
        db.session.add(new_todo)
        db.session.commit()
        return redirect('/')
    except:
        return redirect('/')


@app.route('/delete/<int:id>')
def delete(id):
    todo_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(todo_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return redirect('/')


@app.route('/clear')
def clear():
    todos = Todo.query.all()
    try:
        for todo in todos:
            todo_to_delete = Todo.query.get_or_404(todo.id)
            db.session.delete(todo_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
