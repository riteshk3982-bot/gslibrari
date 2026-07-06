from flask import Flask, render_template, request, redirect, url_for, session
from model import db, Student, Book, Fee, Seat
import random
from werkzeug.utils import secure_filename
import requests
import os

app = Flask(__name__)
# -------- Admin Login --------
DIRECTOR_ID = "GS-DIR-2026-0001"
DIRECTOR_PASSWORD = "GSLibrary@123"

app.config["SECRET_KEY"] = "librarysecret"
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "library.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

def send_otp(mobile, otp):

    url = "https://www.fast2sms.com/dev/bulkV2"

    headers = {
        "authorization": "YOUR_API_KEY"
    }

    data = {
        "route": "otp",
        "variables_values": otp,
        "numbers": mobile
    }

    requests.post(url, headers=headers, data=data)
# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")

# ---------------- ADMIN LOGIN ----------------

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == DIRECTOR_ID and password == DIRECTOR_PASSWORD:

            session["director"] = True

            return redirect(url_for("director_dashboard"))

        else:

            return "Invalid Admin Login"

    return render_template("admin_login.html")

# ---------------- NEW REGISTRATION ----------------

@app.route("/new-registration", methods=["GET", "POST"])
def new_registration():

    if request.method == "POST":

        mobile = request.form["mobile"]

        existing = Student.query.filter_by(mobile=mobile).first()

        if existing:
            return "This Mobile Number is Already Registered."

        session["mobile"] = mobile

        return redirect(url_for("register"))

    return render_template("new_registration.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        mobile = request.form["mobile"]
        password = request.form["password"]

        student = Student.query.filter_by(
            mobile=mobile,
            password=password
        ).first()

        if student:

            session["mobile"] = student.mobile

            return redirect(url_for("dashboard"))

        else:

            return "Wrong Mobile Number or Password"

    return render_template("login.html")


# ---------------- VERIFY OTP ----------------

@app.route("/verify", methods=["GET", "POST"])
def verify():

    if request.method == "POST":

        userotp = request.form["otp"]

        if userotp == session.get("otp"):
            return redirect(url_for("register"))
        else:
            return "Wrong OTP"

    return render_template("verify.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        existing = Student.query.filter_by(mobile=session["mobile"]).first()

        if existing:
            return redirect(url_for("dashboard"))

        photo = request.files["photo"]

        filename = "default.png"

        if photo and photo.filename != "":
            filename = secure_filename(photo.filename)

            photo.save(
                os.path.join(
                    "static",
                    "student_photos",
                    filename
                )
            )
        print("Uploaded File:", filename)

        student = Student(
            mobile=session["mobile"],
            password=request.form["password"],
            photo=filename,
            name=request.form["name"],
            father=request.form["father"],
            mother=request.form["mother"],
            address=request.form["address"],
            shift=request.form["shift"],
            seat=request.form["seat"]
        )

        print("Saved Photo:", student.photo)

        db.session.add(student)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("register.html")


# ---------------- DASHBOARD ----------------



@app.route("/dashboard")
def dashboard():


    student = Student.query.filter_by(
        mobile=session["mobile"]
    ).first()

    return render_template(
        "dashboard.html",
        student=student
    )

# ---------------- ALL STUDENTS ----------------
@app.route("/students")
def students():

    all_students = Student.query.all()

    return render_template(
        "students.html",
        students=all_students
    )
# -----search student----
from sqlalchemy import or_

@app.route("/search-student")
def search_student():

    keyword = request.args.get("keyword")

    students = Student.query.filter(
        or_(
            Student.name.contains(keyword),
            Student.mobile.contains(keyword),
            Student.seat.contains(keyword)
        )
    ).all()

    return render_template(
        "students.html",
        students=students
    )
# ---------------- CHANGE SEAT ----------------

@app.route("/changeseat/<int:id>", methods=["GET", "POST"])
def changeseat(id):

    student = Student.query.get_or_404(id)

    if request.method == "POST":

        student.seat = request.form["seat"]

        db.session.commit()

        return redirect(url_for("students"))

    return render_template(
        "changeseat.html",
        student=student
    )
# ---------------- ADD BOOK ----------------

@app.route("/addbook", methods=["GET", "POST"])
def addbook():

    if request.method == "POST":

        book = Book(
            book_name=request.form["book_name"],
            author=request.form["author"],
            category=request.form["category"],
            quantity=request.form["quantity"]
        )

        db.session.add(book)
        db.session.commit()

        return redirect(url_for("books"))

    return render_template("addbook.html")


# ---------------- BOOKS ----------------

@app.route("/books")
def books():

    all_books = Book.query.all()

    return render_template(
        "books.html",
        books=all_books
    )
# ---------------- STUDENT ID CARD ----------------
@app.route("/idcard/<int:id>")
def idcard(id):

    student = Student.query.get_or_404(id)

    return render_template(
        "idcard.html",
        student=student
    )

@app.route("/my-idcard")
def my_idcard():

    student = Student.query.filter_by(
        mobile=session["mobile"]
    ).first()

    if not student:
        return redirect(url_for("login"))

    return render_template(
        "idcard.html",
        student=student
    )
# ------ delete student----
@app.route("/delete-student/<int:id>")
def delete_student(id):

    student = Student.query.get_or_404(id)

    db.session.delete(student)
    db.session.commit()

    return redirect(url_for("students"))

@app.route("/edit-student/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    student = Student.query.get_or_404(id)

    if request.method == "POST":

        student.name = request.form["name"]
        student.mobile = request.form["mobile"]
        student.father = request.form["father"]
        student.mother = request.form["mother"]
        student.address = request.form["address"]
        student.shift = request.form["shift"]
        student.seat = request.form["seat"]

        db.session.commit()

        return redirect(url_for("students"))

    return render_template(
        "edit_student.html",
        student=student
    )
# ---------------- FEE RECEIPT ----------------

@app.route("/receipt")
def receipt():

    student = Student.query.filter_by(
        mobile=session["mobile"]
    ).first()

    fee = Fee.query.filter_by(
        mobile=session["mobile"]
    ).order_by(Fee.id.desc()).first()

    return render_template(
        "receipt.html",
        student=student,
        fee=fee
    )
# ---------------- DIRECTOR DASHBOARD ----------------

@app.route("/director-dashboard")
def director_dashboard():

    if "director" not in session:
        return redirect(url_for("admin"))

    students = Student.query.all()
    books = Book.query.all()
    fees = Fee.query.all()

    return render_template(
        "director_dashboard.html",
        students=students,
        books=books,
        fees=fees
    )
# -----logout-----
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))
# ---------------- PAYMENT ----------------

@app.route("/payment", methods=["GET", "POST"])
def payment():

    student = Student.query.filter_by(
        mobile=session["mobile"]
    ).first()

    if request.method == "POST":

        file = request.files["screenshot"]

        filename = ""

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(app.root_path, "static", "payments")

            os.makedirs(upload_folder, exist_ok=True)

            file.save(os.path.join(upload_folder, filename))

        fee = Fee(
            mobile=student.mobile,
            month=request.form["month"],
            amount=request.form["amount"],
            status="Pending",
            screenshot=filename
        )

        db.session.add(fee)
        db.session.commit()
        print(fee.mobile)
        print(fee.month)
        print(fee.amount)
        print(fee.status)
        print(fee.screenshot)

        return redirect(url_for("paymenthistory"))

    return render_template(
        "payment.html",
        student=student
    )
# ------history-------
@app.route("/paymenthistory")
def paymenthistory():

    fees = Fee.query.filter_by(
        mobile=session["mobile"]
    ).all()

    return render_template(
        "paymenthistory.html",
        fees=fees
    )

# ---------------- FORGOT PASSWORD ----------------

@app.route("/forgot", methods=["GET", "POST"])
def forgot():

    if request.method == "POST":

        mobile = request.form["mobile"]

        student = Student.query.filter_by(mobile=mobile).first()

        if student:

            otp = str(random.randint(100000, 999999))

            session["reset_mobile"] = mobile
            session["reset_otp"] = otp

            print("Reset OTP :", otp)

            return redirect(url_for("verify_reset_otp"))

        else:

            return "Mobile Number Not Registered"

    return render_template("forgot.html")
# ---------------- VERIFY RESET OTP ----------------

@app.route("/verify-reset-otp", methods=["GET", "POST"])
def verify_reset_otp():

    if request.method == "POST":

        userotp = request.form["otp"]

        if userotp == session.get("reset_otp"):

            return redirect(url_for("new_password"))

        else:

            return "Wrong OTP"

    return render_template("verify_reset_otp.html")

# ---------------- NEW PASSWORD ----------------

@app.route("/new-password", methods=["GET", "POST"])
def new_password():

    if request.method == "POST":

        student = Student.query.filter_by(
            mobile=session["reset_mobile"]
        ).first()

        student.password = request.form["password"]

        db.session.commit()

        session.pop("reset_mobile", None)
        session.pop("reset_otp", None)

        return redirect(url_for("login"))

    return render_template("new_password.html")

# @app.route("/verify-msg91", methods=["POST"])
# def verify_msg91():
#
#     mobile = request.form.get("mobile")
#     access_token = request.form.get("access_token")
#     print("Mobile:", mobile)
#     print("Access Token from Form:", access_token)
#
#     url = "https://control.msg91.com/api/v5/widget/verifyAccessToken"
#
#     headers = {
#         "Content-Type": "application/json"
#     }
#
#     data = {
#         "authkey": "547607ACfdLtbMgRT6a49e83dP1",
#         "access-token": access_token
#     }
#
#     response = requests.post(url, json=data, headers=headers)
#
#     result = response.json()
#
#     print("MSG91 Response:", result)
#     print("Access Token:", access_token)
#     print("Response:", response.status_code)
#     print("Response Body:", response.text)
#
#     if result.get("type") == "success":
#
#         session["mobile"] = mobile
#
#         return redirect(url_for("register"))
#
#     return str(result)
# ---------------- RUN ----------------

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5000, debug=True)



