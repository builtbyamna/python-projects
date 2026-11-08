
from flask import Flask, render_template, request
import sqlite3
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

DATABASE = Path(__file__).with_name("appointments.db")


def connect():
    return sqlite3.connect(DATABASE)


def create_database():
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                service TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                UNIQUE(appointment_date, appointment_time)
            )
        """)


@app.route("/", methods=["GET", "POST"])
def home():
    error = None

    services = [
        "Consultation",
        "Meeting",
        "Personal Session",
        "Other"
    ]

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        service = request.form.get("service", "")
        day = request.form.get("date", "")
        time = request.form.get("time", "")

        try:
            appointment = datetime.strptime(
                day + " " + time, "%Y-%m-%d %H:%M"
            )

            if not name or not email or "@" not in email:
                error = "Please enter a valid name and email."

            elif service not in services:
                error = "Please choose a valid service."

            elif appointment <= datetime.now():
                error = "Please choose a future date and time."

            else:
                with connect() as db:
                    db.execute("""
                        INSERT INTO appointments
                        (name, email, service, appointment_date, appointment_time)
                        VALUES (?, ?, ?, ?, ?)
                    """, (name, email, service, day, time))

                time_12 = appointment.strftime("%I:%M %p")

                return render_template(
                    "success.html",
                    name=name,
                    service=service,
                    day=day,
                    time=time_12
                )

        except ValueError:
            error = "Please enter a valid date and time."

        except sqlite3.IntegrityError:
            error = "That time is already booked. Please choose another."

    return render_template(
        "index.html",
        error=error,
        today=datetime.now().strftime("%Y-%m-%d")
    )


if __name__ == "__main__":
    create_database()
    app.run(debug=True)