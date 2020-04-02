from flask import Blueprint, render_template, request, redirect, url_for, g, flash, session
import datetime
from . import db
from werkzeug.exceptions import abort


from flasktodo.auth import login_required


bp = Blueprint("todos", __name__)

@bp.route("/")
def index():
    """View for home page which shows list of to-do items."""
    #session['users_id'] = users['id']
    #user_id = session['users_id']
    cur = db.get_db().cursor()
    cur.execute("""SELECT todos.user_id, users.id, todos.description FROM todos
    JOIN users ON todos.user_id = users.id""")

    todos = cur.fetchall()

    cur.close()


    return render_template("index.html", todos=todos)

@bp.route("/completed")
def index_completed():
    """View for home page which shows list of completed to-do items."""

    cur = db.get_db().cursor()
    cur.execute("""
     SELECT * FROM todos
     WHERE completed = 'True';""")
    todos = cur.fetchall()
    cur.close()

    return render_template("index.html", todos=todos)

@bp.route("/not_completed")
def index_not_completed():
    """View for home page which shows list of not completed to-do items."""

    cur = db.get_db().cursor()
    cur.execute("""
     SELECT * FROM todos
     WHERE completed = 'False';""")
    todos = cur.fetchall()
    cur.close()

    return render_template("index.html", todos=todos)

@bp.route("/mark/<id>")
def mark(id):
    """Marks an item as completed"""

    cur = db.get_db().cursor()
    cur.execute("""
     UPDATE todos SET completed = True
     WHERE id = %s;
     """,
        (id,))
    db.get_db().commit()
    cur.execute('SELECT * FROM todos')
    todos = cur.fetchall()
    cur.close()

    return render_template("index.html", todos=todos)

@bp.route("/delete/<id>")
def delete(id):
    """Deletes an item"""

    cur = db.get_db().cursor()
    cur.execute("""
     DELETE FROM todos
     WHERE id = %s;
     """,
        (id,))
    db.get_db().commit()
    cur.execute('SELECT * FROM todos')
    todos = cur.fetchall()
    cur.close()

    return render_template("index.html", todos=todos)

@bp.route("/create-item", methods=('GET', 'POST'))
def create():
    """View for create page which allows you to create the list items."""
    if request.method == 'POST':
        item = request.form['description']
        dt = datetime.datetime.now()

        cur = db.get_db().cursor()
        cur.execute("""
         INSERT INTO todos (description, completed, created_at, user_id)
         VALUES (%s, %s, %s, %s);
         """,
         (item, False, dt, g.users['id']))
        db.get_db().commit()
        cur.close()

        return redirect(url_for('todos.index'))
    return render_template('create.html')

@bp.route("/update/<id>", methods=('GET', 'POST'))
def update(id):
    """view for the update page which allows you to edit an item"""
    if request.method =='POST':
        item = request.form['description']

        cur = db.get_db().cursor()
        cur.execute("""
        UPDATE todos SET description = %s
        WHERE id = %s;
        """,
            (item, id))
        db.get_db().commit()
        cur.close()

        return redirect(url_for('todos.index'))
    return render_template('update.html')
