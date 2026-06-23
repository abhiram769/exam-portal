from flask import Flask, render_template, request, redirect, session
from config import Config
import sqlite3
import os
import razorpay

app = Flask(__name__)
app.config.from_object(Config)

app.secret_key = Config.SECRET_KEY

client = razorpay.Client(
    auth=(
        Config.RAZORPAY_KEY_ID,
        Config.RAZORPAY_SECRET
    )
)


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
    amount = int(request.form["amount"])

    order = client.order.create({
        "amount": amount * 100,
        "currency": "INR"
    })

    conn = sqlite3.connect("payments.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO payments
        (name, phone, telegram, amount, order_id, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            phone,
            telegram,
            amount,
            order["id"],
            "Pending"
        )
    )

    conn.commit()
    conn.close()

    return render_template(
        "checkout.html",
        order_id=order["id"],
        amount=amount,
        amount_paise=amount * 100,
        razorpay_key=Config.RAZORPAY_KEY_ID
    )


@app.route("/verify-payment", methods=["POST"])
def verify_payment():

    payment_id = request.form["payment_id"]
    order_id = request.form["order_id"]
    signature = request.form["signature"]

    try:

        client.utility.verify_payment_signature({
            "razorpay_payment_id": payment_id,
            "razorpay_order_id": order_id,
            "razorpay_signature": signature
        })

        conn = sqlite3.connect("payments.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE payments
            SET payment_id=?,
                status='Paid'
            WHERE order_id=?
            """,
            (
                payment_id,
                order_id
            )
        )

        conn.commit()
        conn.close()

        return redirect("/success")

    except Exception as e:
        return f"Payment Verification Failed: {e}"


@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if (
            username == Config.ADMIN_USERNAME
            and
            password == Config.ADMIN_PASSWORD
        ):

            session["admin"] = True
            return redirect("/admin/dashboard")

        return "Invalid Username or Password"

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():

    if not session.get("admin"):
        return redirect("/admin/login")

    conn = sqlite3.connect("payments.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            phone,
            telegram,
            amount,
            payment_id,
            order_id,
            status,
            payment_date
        FROM payments
        ORDER BY id DESC
    """)

    payments = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        payments=payments
    )


@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect("/admin/login")
@app.route("/admin/clear-db")
def clear_db():

    conn = sqlite3.connect("payments.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM payments")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='payments'")

    conn.commit()
    conn.close()

    return "Database Cleared Successfully"


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )