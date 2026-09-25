"""Task 4.2: a minimal Python web application."""
import platform
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

STUDENT_NAME = "CHEONG EN YING"
STUDENT_ID = "105965515"


@app.get("/")
def index():
    return render_template_string("""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Task 4.2 — Hello World</title>
    </head>
    <body>
        <h1>Hello World!</h1>
        <p>Task 4.2: Python + Flask running in Docker.</p>
        <hr>
        <p><strong>Student:</strong> {{ student_name }}</p>
        <p><strong>Student ID:</strong> {{ student_id }}</p>
        <p><strong>Unit:</strong>
            SWE40006 Software Deployment and Evolution
        </p>
    </body>
    </html>
    """, student_name=STUDENT_NAME, student_id=STUDENT_ID)


@app.get("/health")
def health():
    return jsonify(
        status="ok",
        app="hello-web",
        python=platform.python_version()
    )