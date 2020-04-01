import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from . import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        cur = db.get_db().cursor()

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif cur.execute(
            """SELECT id FROM users WHERE email = %s""", (email,)
        ) and cur.fetchone() is not None:
            error = 'user {} is already registered.'.format(email)

        if error is None:
            cur.execute(
                'INSERT INTO users (email, password) VALUES (%s, %s)',
                (email, generate_password_hash(password))
            )
            db.get_db().commit()
            cur.close()
            return redirect(url_for('auth.login'))

        flash(error)
        cur.close()

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        cur = db.get_db().cursor()
        cur.execute(
            'SELECT * FROM users WHERE email = %s', (email,)
        )
        user = cur.fetchone()

        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['users_id'] = user['id']
            return redirect(url_for('todos.index'))

        cur.close()

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_users():
    users_id = session.get('users_id')
    cur = db.get_db().cursor()

    if users_id is None:
        g.users = None
    else:
        g.users = cur.execute(
            'SELECT * FROM users WHERE id = %s', (users_id,)
        )
        cur.fetchone()
        cur.close()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.users is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
