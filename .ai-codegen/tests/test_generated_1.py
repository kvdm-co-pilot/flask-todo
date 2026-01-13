from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pytest

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean, default=False)


@app.route("/")
def home():
    todo_list = Todo.query.all()
    return render_template("base.html", todo_list=todo_list)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/update/<int:todo_id>", methods=["POST"])
def update(todo_id):
    todo = Todo.query.get(todo_id)
    todo.title = request.form.get("title", todo.title)
    todo.complete = "completed" in request.form
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.get(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
        yield client


def test_home_loads_successfully_returns_200(client):
    res = client.get("/")
    assert res.status_code == 200


def test_add_route_creates_todo_in_database(client):
    payload = {"title": "Integration Task"}
    client.post("/add", data=payload)
    with app.app_context():
        todos = Todo.query.all()
        assert len(todos) == 1
        assert todos[0].title == "Integration Task"


def test_update_route_updates_todo(client):
    with app.app_context():
        todo = Todo(title="Before", complete=False)
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
    client.post(f"/update/{todo_id}", data={"title": "After", "completed": "on"})
    with app.app_context():
        updated = Todo.query.get(todo_id)
        assert updated.title == "After"
        assert updated.complete is True


def test_delete_route_removes_item(client):
    with app.app_context():
        todo = Todo(title="Delete Me", complete=False)
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
    client.get(f"/delete/{todo_id}")
    with app.app_context():
        remaining = Todo.query.get(todo_id)
        assert remaining is None


def test_home_shows_created_todos(client):
    with app.app_context():
        db.session.add(Todo(title="Visible", complete=False))
        db.session.commit()
    res = client.get("/")
    assert b"Visible" in res.data