from flask import Flask, render_template
from config import Config
from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)
app.config.from_object(Config)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

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

    return f"""
    <h1>Registration Received</h1>

    <p>Name: {name}</p>

    <p>Next Step: Payment Gateway</p>
    """

if __name__ == "__main__":
    app.run(debug=True)