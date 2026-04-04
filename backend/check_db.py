import sqlite3

def check_db():
    conn = sqlite3.connect('gigshield_production.db')
    cursor = conn.cursor()
    
    print("--- USERS ---")
    cursor.execute("SELECT id, phone, name, role FROM users")
    for row in cursor.fetchall():
        print(row)
        
    print("\n--- CLAIMS ---")
    cursor.execute("SELECT id, user_id, order_id, status, trigger_event FROM claims")
    claims = cursor.fetchall()
    if not claims:
        print("No claims found in database.")
    for row in claims:
        print(row)
        
    print("\n--- ORDERS ---")
    cursor.execute("SELECT id, user_id FROM orders")
    for row in cursor.fetchall():
        print(row)
        
    conn.close()

if __name__ == "__main__":
    check_db()
