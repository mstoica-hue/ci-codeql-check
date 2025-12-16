import os
import sqlite3
import pickle
import subprocess
from flask import Flask, request, render_template, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "dev-secret"   # necesar pentru flash
DATABASE = "users.db"


# =========================
# Database helpers
# =========================
def get_db():
    return sqlite3.connect(DATABASE)


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
    )
    conn.commit()
    conn.close()


# =========================
# UI
# =========================
@app.route("/")
def index():
    return render_template("index.html")


# =========================
# SQL Injection
# =========================
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    conn = get_db()
    cur = conn.cursor()
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cur.execute(query)
    user = cur.fetchone()
    conn.close()

    if user:
        flash("Login successful", "success")
    else:
        flash("Invalid credentials", "error")

    return redirect(url_for("index"))


# =========================
# Command Injection
# =========================
@app.route("/ping", methods=["POST"])
def ping():
    host = request.form.get("host")
    os.system(f"ping -c 1 {host}")
    flash(f"Ping executed for host: {host}", "info")
    return redirect(url_for("index"))


# =========================
# Path Traversal
# =========================
@app.route("/read", methods=["POST"])
def read_file():
    filename = request.form.get("file")
    try:
        with open(filename, "r") as f:
            content = f.read()
        flash(f"File '{filename}' read successfully", "success")
    except Exception as e:
        flash(f"Error reading file: {e}", "error")

    return redirect(url_for("index"))


# =========================
# Insecure Deserialization
# =========================
@app.route("/load", methods=["POST"])
def load_object():
    try:
        data = request.form.get("data").encode()
        obj = pickle.loads(data)
        flash(f"Object loaded: {obj}", "success")
    except Exception as e:
        flash(f"Deserialization error: {e}", "error")

    return redirect(url_for("index"))


# =========================
# Broken Access Control
# =========================
SECRET_KEY = "super-secret-key"

@app.route("/admin", methods=["POST"])
def admin():
    token = request.form.get("token")
    if token == SECRET_KEY:
        flash("Welcome admin", "success")
    else:
        flash("Unauthorized access", "error")

    return redirect(url_for("index"))


# =========================
# Unsafe subprocess
# =========================
@app.route("/run", methods=["POST"])
def run_command():
    cmd = request.form.get("cmd")
    subprocess.run(cmd, shell=True)
    flash(f"Command executed: {cmd}", "warning")
    return redirect(url_for("index"))


# =========================
# Entry point
# =========================
if __name__ == "__main__":
    init_db()
    app.run(debug=True, use_reloader=False)
