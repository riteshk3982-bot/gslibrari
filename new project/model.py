from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    mobile = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    name = db.Column(db.String(100), nullable=False)
    father = db.Column(db.String(100), nullable=False)
    mother = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    shift = db.Column(db.String(20), nullable=False)
    seat = db.Column(db.String(20), nullable=False)

    photo = db.Column(db.String(200), default="default.png")

# ---book management---
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    book_name = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)



# ---------------- FEE ----------------

class Fee(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    mobile = db.Column(db.String(15), nullable=False)

    amount = db.Column(db.Integer, nullable=False)

    month = db.Column(db.String(30), nullable=False)

    status = db.Column(db.String(20), default="Pending")
    screenshot = db.Column(db.String(200))

# ---------------- SEAT ----------------

class Seat(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    seat_no = db.Column(db.String(10), unique=True, nullable=False)
    photo = db.Column(db.String(200), default="default.png")

    shift = db.Column(db.String(20), nullable=False)

    status = db.Column(db.String(20), default="Available")