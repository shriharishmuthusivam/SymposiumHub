import sqlite3

def reset_student_data():
    conn = sqlite3.connect('symposium.db')
    cur = conn.cursor()

    # ❌ Delete all event registrations
    cur.execute("DELETE FROM event_registrations")

    # ❌ Delete all student login accounts
    cur.execute("DELETE FROM users")

    conn.commit()
    conn.close()

    print("✅ All student registrations and event data deleted successfully!")

if __name__ == "__main__":
    reset_student_data()
