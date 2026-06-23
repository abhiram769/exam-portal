import sqlite3

conn = sqlite3.connect("payments.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS payments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    telegram TEXT NOT NULL,
    payment_id TEXT,
    order_id TEXT,
    amount INTEGER,
    status TEXT,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("Database Created")