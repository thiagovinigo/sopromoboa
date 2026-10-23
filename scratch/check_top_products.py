import sqlite3

conn = sqlite3.connect('c:/Users/User/sopromoboa/backend/sopromoboa.db')
cur = conn.cursor()
terms = ['Echo', 'Alexa', 'Fire TV', 'Kindle', 'Creatina', 'Whey', 'Air Fryer', 'Airfryer', 'JBL', 'Nespresso', 'Aspirador']
for term in terms:
    cur.execute("SELECT count(*) FROM products WHERE title LIKE ?", (f"%{term}%",))
    print(f"{term}: {cur.fetchone()[0]} items")
conn.close()
