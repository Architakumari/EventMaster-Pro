from flask import Flask, request, jsonify, send_from_directory
import sqlite3

app = Flask(__name__)

# ===== DATABASE CONNECTION =====
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# ===== DATABASE INIT =====
def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Events table
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            venue TEXT NOT NULL,
            description TEXT NOT NULL,
            total_tickets INTEGER NOT NULL DEFAULT 150,
            theme_color TEXT DEFAULT '#f97316',
            image_url TEXT DEFAULT 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80'
        )
    ''')

    # Tickets table
    c.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            event TEXT NOT NULL,
            name TEXT NOT NULL,
            num INTEGER NOT NULL,
            FOREIGN KEY(event_id) REFERENCES events(id)
        )
    ''')

    # Add missing columns for older databases
    try: c.execute("ALTER TABLE events ADD COLUMN total_tickets INTEGER NOT NULL DEFAULT 150")
    except: pass
    try: c.execute("ALTER TABLE tickets ADD COLUMN event_id INTEGER")
    except: pass
    try: c.execute("ALTER TABLE events ADD COLUMN theme_color TEXT DEFAULT '#f97316'")
    except: pass
    try: c.execute("ALTER TABLE events ADD COLUMN image_url TEXT DEFAULT 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80'")
    except: pass

    conn.commit()
    conn.close()

# ===== CREATE MISSING EVENTS FROM OLD TICKETS =====
def create_missing_events_from_tickets():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT DISTINCT tickets.event
        FROM tickets
        LEFT JOIN events ON tickets.event = events.name
        WHERE events.id IS NULL
    """)
    missing_events = c.fetchall()

    for row in missing_events:
        c.execute("""
            INSERT INTO events (name, date, time, venue, description, total_tickets, theme_color, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (row["event"], "2026-12-31", "18:00", "TBA", "Legacy Event", 150, "#8b5cf6", "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80"))

    conn.commit()
    conn.close()

# ===== FIX OLD BOOKINGS =====
def repair_old_ticket_links():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE tickets SET event_id = (SELECT events.id FROM events WHERE events.name = tickets.event LIMIT 1)
        WHERE event_id IS NULL
    """)
    conn.commit()
    conn.close()

init_db()
create_missing_events_from_tickets()
repair_old_ticket_links()

# ===== PAGES =====
@app.route("/")
def home(): return send_from_directory(".", "index.html")

@app.route("/create")
def create_page(): return send_from_directory(".", "create.html")

@app.route("/booking")
def booking_page(): return send_from_directory(".", "booking.html")

@app.route("/dashboard")
def dashboard_page(): return send_from_directory(".", "dashboard.html")

# ===== DASHBOARD API =====
@app.route("/api/stats", methods=["GET"])
def get_stats():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT e.name, COALESCE(SUM(t.num), 0) AS total_booked FROM events e LEFT JOIN tickets t ON e.id = t.event_id GROUP BY e.id")
    rows = c.fetchall()
    conn.close()
    return jsonify({"labels": [r["name"] for r in rows], "data": [r["total_booked"] for r in rows]})

# ===== EVENTS =====
@app.route("/events", methods=["GET"])
def get_events():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT e.*, COALESCE(SUM(t.num), 0) AS booked
        FROM events e LEFT JOIN tickets t ON e.id = t.event_id
        GROUP BY e.id HAVING booked < e.total_tickets ORDER BY e.id DESC
    """)
    rows = c.fetchall()
    conn.close()

    events = []
    for r in rows:
        events.append({
            "id": r["id"], "name": r["name"], "date": r["date"], "time": r["time"],
            "venue": r["venue"], "description": r["description"], 
            "total_tickets": r["total_tickets"], "booked": r["booked"], 
            "remaining": r["total_tickets"] - r["booked"],
            "theme_color": r["theme_color"], "image_url": r["image_url"]
        })
    return jsonify(events)

@app.route("/events", methods=["POST"])
def create_event():
    data = request.json
    if not all(k in data for k in ("name", "date", "time", "venue", "description")):
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO events (name, date, time, venue, description, total_tickets, theme_color, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"], data["date"], data["time"], data["venue"], data["description"], 
        150, data.get("theme_color", "#f97316"), data.get("image_url", "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80")
    ))
    conn.commit()
    conn.close()
    return jsonify({"message": "Event created successfully"})

@app.route("/events/<int:id>", methods=["DELETE"])
def delete_event(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM events WHERE id = ?", (id,))
    c.execute("DELETE FROM tickets WHERE event_id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Event deleted successfully"})

# ===== TICKETS =====
@app.route("/tickets", methods=["GET"])
def get_tickets():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM tickets ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"event": r["event"], "name": r["name"], "num": r["num"]} for r in rows])

@app.route("/tickets", methods=["POST"])
def book_ticket():
    data = request.json
    event_id, num = int(data["event_id"]), int(data["num"])

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT total_tickets, name FROM events WHERE id = ?", (event_id,))
    event_row = c.fetchone()
    
    if not event_row: return jsonify({"error": "Event not found"}), 404
    
    c.execute("SELECT COALESCE(SUM(num), 0) AS booked FROM tickets WHERE event_id = ?", (event_id,))
    remaining = event_row["total_tickets"] - c.fetchone()["booked"]

    if num > remaining: return jsonify({"error": f"Only {remaining} ticket(s) left"}), 400

    c.execute("INSERT INTO tickets (event_id, event, name, num) VALUES (?, ?, ?, ?)", 
              (event_id, data["event"], data["name"], num))
    conn.commit()
    conn.close()
    return jsonify({"message": "Ticket booked successfully"})

if __name__ == "__main__":
    app.run(debug=True)