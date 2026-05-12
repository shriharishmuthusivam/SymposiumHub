import sqlite3

conn = sqlite3.connect('symposium.db')
cur = conn.cursor()

cur.execute("DELETE FROM events")

events = [
    'AI Quiz',
    'AI Prompt Creation',
    'Debugging',
    'Tech-Connection',
    'Adzap',
    'IPL Auction',
    'Dumb Charades',
    'Memory Matrix'
]

for e in events:
    cur.execute("INSERT INTO events (event_name) VALUES (?)", (e,))

conn.commit()
conn.close()

print("✅ Events updated successfully")
