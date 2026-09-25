"""A small shared study board. Use demonstration data, not private records."""
import hmac
import os
import secrets
import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path

from flask import Flask, abort, g, jsonify, redirect, render_template, request, session, url_for


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        DATABASE=os.environ.get('DATABASE_PATH', '/data/tasks.db'),
        MAX_CONTENT_LENGTH=16 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )
    if test_config:
        app.config.update(test_config)
    if not app.config['SECRET_KEY']:
        raise RuntimeError('SECRET_KEY must be set before starting the study manager.')

    Path(app.config['DATABASE']).parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(app.config['DATABASE'])) as db:
        db.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL, subject TEXT NOT NULL,
            due_date TEXT NOT NULL, priority TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0,1)))''')
        db.commit()

    def database():
        if 'db' not in g:
            g.db = sqlite3.connect(app.config['DATABASE'], timeout=10)
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_database(error=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    @app.before_request
    def check_csrf():
        if request.method == 'POST':
            expected = session.get('csrf', '')
            supplied = request.form.get('csrf', '')
            if not expected or not hmac.compare_digest(expected, supplied):
                abort(400, description='Form expired or invalid. Reload the page and try again.')

    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self'; form-action 'self'; frame-ancestors 'none'"
        return response

    def page(error=None, status=200):
        session.setdefault('csrf', secrets.token_hex(32))
        tasks = database().execute('SELECT * FROM tasks ORDER BY completed, due_date, id').fetchall()
        return render_template('index.html', tasks=tasks, error=error, values=request.form,
                               today=date.today().isoformat(), csrf=session['csrf']), status

    @app.get('/')
    def index():
        return page()

    @app.post('/tasks')
    def add():
        name = request.form.get('name', '').strip()
        subject = request.form.get('subject', '').strip()
        due = request.form.get('due_date', '')
        priority = request.form.get('priority', '')
        try:
            if not 1 <= len(name) <= 120 or not 1 <= len(subject) <= 60:
                raise ValueError('Task name (1-120 characters) and subject (1-60) are required.')
            if date.fromisoformat(due).isoformat() != due:
                raise ValueError('Use a due date in YYYY-MM-DD format.')
            if priority not in ('Low', 'Medium', 'High'):
                raise ValueError('Select Low, Medium or High priority.')
        except ValueError as error:
            app.logger.warning('Task validation rejected: %s', error)
            return page(str(error), 400)
        db = database()
        db.execute('INSERT INTO tasks (name, subject, due_date, priority) VALUES (?, ?, ?, ?)',
                   (name, subject, due, priority))
        db.commit()
        app.logger.info('Task added')
        return redirect(url_for('index'), code=303)

    @app.post('/tasks/<int:task_id>/complete')
    def complete(task_id):
        db = database()
        cursor = db.execute('UPDATE tasks SET completed=1 WHERE id=?', (task_id,))
        if not cursor.rowcount:
            abort(404)
        db.commit()
        return redirect(url_for('index'), code=303)

    @app.post('/tasks/<int:task_id>/delete')
    def delete(task_id):
        db = database()
        cursor = db.execute('DELETE FROM tasks WHERE id=?', (task_id,))
        if not cursor.rowcount:
            abort(404)
        db.commit()
        return redirect(url_for('index'), code=303)

    @app.get('/health')
    def health():
        database().execute('SELECT COUNT(*) FROM tasks').fetchone()
        return jsonify(status='ok', app='study-manager', storage='sqlite')

    return app
