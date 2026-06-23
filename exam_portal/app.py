from flask import Flask, render_template, request
from config import Config
import sqlite3
import os

app = Flask(__name__)
app.config.from_object(Config)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/payment")
def payment():
    return render_template("payment.html")


@app.route("/register", methods=["POST"])
def register():

    name = request.form["name"]
    phone = request.form["phone"]
    telegram = request.form["telegram"]

    conn = sqlite3.connect("payments.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO payments
    (name, phone, telegram, amount, status)
    VALUES (?, ?, ?, ?, ?)
    """,
    (name, phone, telegram, 99, "Pending"))

    conn.commit()
    conn.close()

    return render_template("success.html")


@app.route("/success")
def success():
    return render_template("success.html")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )