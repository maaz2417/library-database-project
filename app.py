from flask import Flask, request, redirect, render_template
import mysql.connector
import re

app = Flask(__name__)

# CONNECT TO MYSQL
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="rms222005",   # put your MySQL password here
        database="library_db2"
    )

# ─────────────────────────────────────────────
# DASHBOARD PAGE
# ─────────────────────────────────────────────
@app.route("/")
def index():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS v FROM books")
    total = cur.fetchone()["v"]
    cur.execute("SELECT COALESCE(SUM(quantity), 0) AS v FROM books")
    copies = cur.fetchone()["v"]
    cur.execute("SELECT COALESCE(SUM(available), 0) AS v FROM books")
    available = cur.fetchone()["v"]
    cur.execute("SELECT COUNT(*) AS v FROM books WHERE available = 0")
    out_of_stock = cur.fetchone()["v"]
    cur.execute("SELECT * FROM books ORDER BY book_id DESC LIMIT 5")
    recent = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("dashboard.html", 
                           total=total, 
                           copies=copies, 
                           available=available, 
                           out_of_stock=out_of_stock, 
                           recent=recent)


# ─────────────────────────────────────────────
# ALL BOOKS PAGE
# ─────────────────────────────────────────────
@app.route("/books")
def books():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    page_num = max(1, request.args.get("page", 1, type=int))
    per_page = 8
    offset   = (page_num - 1) * per_page
    sort = request.args.get("sort", "title")
    if sort not in ["title", "author", "category", "book_id", "available"]:
        sort = "title"
    cur.execute("SELECT COUNT(*) AS v FROM books")
    total = cur.fetchone()["v"]
    total_pages = max(1, -(-total // per_page))
    cur.execute("SELECT * FROM books ORDER BY " + sort + " ASC LIMIT %s OFFSET %s", (per_page, offset))
    all_books = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("books.html", 
                           all_books=all_books, 
                           page_num=page_num, 
                           total_pages=total_pages, 
                           sort=sort)


# ─────────────────────────────────────────────
# ADD BOOK PAGE
# ─────────────────────────────────────────────
@app.route("/add", methods=["GET", "POST"])
def add_book():
    msg = ""
    if request.method == "POST":
        title     = request.form["title"].strip()
        author    = request.form["author"].strip()
        category  = request.form["category"].strip()
        isbn      = request.form["isbn"].strip()
        publisher = request.form["publisher"].strip()
        year      = request.form["year"].strip()
        quantity  = request.form["quantity"].strip()

        if not title or not author or not category or not isbn or not quantity.isdigit() or int(quantity) < 1:
            msg = "<div class='alert-red'>Please fill in all required fields correctly.</div>"
        else:
            conn = get_db()
            cur  = conn.cursor(dictionary=True)
            cur.execute("SELECT book_id FROM books WHERE isbn = %s", (isbn,))
            if cur.fetchone():
                msg = "<div class='alert-red'>A book with this ISBN already exists.</div>"
            else:
                cur.execute(
                    "INSERT INTO books (title, author, category, isbn, publisher, year, quantity, available) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (title, author, category, isbn, publisher,
                     int(year) if year.isdigit() else None,
                     int(quantity), int(quantity))
                )
                conn.commit()
                msg = "<div class='alert-green'>Book added successfully!</div>"
            cur.close()
            conn.close()

    return render_template("add_book.html", msg=msg)


# ─────────────────────────────────────────────
# EDIT BOOK PAGE
# ─────────────────────────────────────────────
@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
    book = cur.fetchone()
    if not book:
        return redirect("/books")

    msg = ""
    if request.method == "POST":
        title     = request.form["title"].strip()
        author    = request.form["author"].strip()
        category  = request.form["category"].strip()
        isbn      = request.form["isbn"].strip()
        publisher = request.form["publisher"].strip()
        year      = request.form["year"].strip()
        quantity  = request.form["quantity"].strip()
        available = request.form["available"].strip()

        if not title or not author or not category or not quantity.isdigit() or int(quantity) < 1:
            msg = "<div class='alert-red'>Please fill in all required fields correctly.</div>"
        elif available.isdigit() and int(available) > int(quantity):
            msg = "<div class='alert-red'>Available cannot be more than quantity.</div>"
        else:
            cur.execute(
                "UPDATE books SET title=%s, author=%s, category=%s, isbn=%s, publisher=%s, year=%s, quantity=%s, available=%s WHERE book_id=%s",
                (title, author, category, isbn, publisher,
                 int(year) if year.isdigit() else None,
                 int(quantity),
                 int(available) if available.isdigit() else 0,
                 book_id)
            )
            conn.commit()
            cur.close()
            conn.close()
            return redirect("/books")

    cur.close()
    conn.close()

    return render_template("edit_book.html", book=book, msg=msg)


# ─────────────────────────────────────────────
# DELETE BOOK
# ─────────────────────────────────────────────
@app.route("/delete/<int:book_id>")
def delete_book(book_id):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/books")


# ─────────────────────────────────────────────
# SEARCH PAGE
# ─────────────────────────────────────────────
@app.route("/search")
def search():
    query     = request.args.get("q", "").strip()
    search_by = request.args.get("by", "all")
    results   = []

    if query:
        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        like = "%" + query + "%"
        if search_by == "title":
            cur.execute("SELECT * FROM books WHERE title LIKE %s", (like,))
        elif search_by == "author":
            cur.execute("SELECT * FROM books WHERE author LIKE %s", (like,))
        elif search_by == "category":
            cur.execute("SELECT * FROM books WHERE category LIKE %s", (like,))
        elif search_by == "isbn":
            cur.execute("SELECT * FROM books WHERE isbn LIKE %s", (like,))
        else:
            cur.execute("SELECT * FROM books WHERE title LIKE %s OR author LIKE %s OR category LIKE %s OR isbn LIKE %s", (like, like, like, like))
        results = cur.fetchall()
        cur.close()
        conn.close()

    return render_template("search.html", query=query, search_by=search_by, results=results)


# ═════════════════════════════════════════════
#  MODULE 2 — MEMBER MANAGEMENT
# ═════════════════════════════════════════════

# ─────────────────────────────────────────────
# VIEW ALL MEMBERS  (GET /members)
# ─────────────────────────────────────────────
@app.route("/members")
def view_members():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM members ORDER BY member_id DESC")
    all_members = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("members.html", all_members=all_members)


# ─────────────────────────────────────────────
# ADD MEMBER PAGE  (GET + POST /add_member → POST /members)
# ─────────────────────────────────────────────
@app.route("/add_member")
def add_member_page():
    # Show the blank add member form
    msg = request.args.get("msg", "")
    alert = ""
    if msg == "duplicate":
        alert = "<div class='alert-red'>A member with this email already exists.</div>"
    elif msg == "invalid":
        alert = "<div class='alert-red'>Please fill in all required fields with a valid email.</div>"

    return render_template("add_member.html", alert=alert)


@app.route("/members", methods=["POST"])
def add_member():
    # Handle the POST: insert new member into DB
    name    = request.form["name"].strip()
    email   = request.form["email"].strip()
    phone   = request.form["phone"].strip()
    address = request.form["address"].strip()

    # Validate: required fields + basic email format check
    email_pattern = r'^[^@]+@[^@]+\.[^@]+$'
    if not name or not email or not re.match(email_pattern, email):
        return redirect("/add_member?msg=invalid")

    conn = get_db()
    cur  = conn.cursor(dictionary=True)

    # Check duplicate email
    cur.execute("SELECT member_id FROM members WHERE email = %s", (email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return redirect("/add_member?msg=duplicate")

    cur.execute(
        "INSERT INTO members (name, email, phone, address) VALUES (%s, %s, %s, %s)",
        (name, email, phone or None, address or None)
    )
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/members")


# ─────────────────────────────────────────────
# GET ONE MEMBER  (GET /members/<id>)
# ─────────────────────────────────────────────
@app.route("/members/<int:member_id>")
def get_member(member_id):
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
    m = cur.fetchone()
    cur.close()
    conn.close()
    if not m:
        return redirect("/members")

    return render_template("view_member.html", m=m)


# ─────────────────────────────────────────────
# EDIT MEMBER PAGE  (GET + PUT /members/<id>)
# ─────────────────────────────────────────────
@app.route("/edit_member/<int:member_id>", methods=["GET", "POST"])
def edit_member(member_id):
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
    m = cur.fetchone()
    if not m:
        cur.close()
        conn.close()
        return redirect("/members")

    msg = ""
    if request.method == "POST":
        name    = request.form["name"].strip()
        email   = request.form["email"].strip()
        phone   = request.form["phone"].strip()
        address = request.form["address"].strip()

        email_pattern = r'^[^@]+@[^@]+\.[^@]+$'
        if not name or not email or not re.match(email_pattern, email):
            msg = "<div class='alert-red'>Please fill in all required fields with a valid email.</div>"
        else:
            # Check duplicate email — but allow the member to keep their own email
            cur.execute("SELECT member_id FROM members WHERE email = %s AND member_id != %s", (email, member_id))
            if cur.fetchone():
                msg = "<div class='alert-red'>Another member already has this email.</div>"
            else:
                cur.execute(
                    "UPDATE members SET name=%s, email=%s, phone=%s, address=%s WHERE member_id=%s",
                    (name, email, phone or None, address or None, member_id)
                )
                conn.commit()
                cur.close()
                conn.close()
                return redirect("/members")

    cur.close()
    conn.close()

    return render_template("edit_member.html", m=m, msg=msg)


# ─────────────────────────────────────────────
# DELETE MEMBER  (DELETE /members/<id>)
# ─────────────────────────────────────────────
@app.route("/delete_member/<int:member_id>")
def delete_member(member_id):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("DELETE FROM members WHERE member_id = %s", (member_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/members")


# ═════════════════════════════════════════════
#  MODULE 3 — ISSUE BOOK
# ═════════════════════════════════════════════

# ─────────────────────────────────────────────
# ISSUE BOOK PAGE  (GET /issue_book)
# ─────────────────────────────────────────────
@app.route("/issue_book")
def issue_book_page():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)

    # Load members and only available books for the dropdowns
    cur.execute("SELECT member_id, name, email FROM members ORDER BY name")
    members = cur.fetchall()
    cur.execute("SELECT book_id, title, author, available FROM books WHERE available > 0 ORDER BY title")
    available_books = cur.fetchall()
    cur.close()
    conn.close()

    msg = request.args.get("msg", "")
    alert = ""
    if msg == "no_book":
        alert = "<div class='alert-red'>Book does not exist or is not available.</div>"
    elif msg == "no_member":
        alert = "<div class='alert-red'>Selected member does not exist.</div>"
    elif msg == "invalid":
        alert = "<div class='alert-red'>Please fill in all required fields.</div>"
    elif msg == "ok":
        alert = "<div class='alert-green'>Book issued successfully!</div>"

    return render_template("issue_book.html", members=members, available_books=available_books, alert=alert)


# ─────────────────────────────────────────────
# ISSUE BOOK — POST  (POST /issue)
# Core logic: validate → insert → reduce quantity
# ─────────────────────────────────────────────
@app.route("/issue", methods=["POST"])
def issue_book():
    member_id  = request.form.get("member_id", "").strip()
    book_id    = request.form.get("book_id", "").strip()
    issue_date = request.form.get("issue_date", "").strip()
    due_date   = request.form.get("due_date", "").strip()

    # Step 1: Validate all fields are present
    if not member_id or not book_id or not issue_date or not due_date:
        return redirect("/issue_book?msg=invalid")

    conn = get_db()
    cur  = conn.cursor(dictionary=True)

    # Step 2: Check if book exists AND has available copies
    cur.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
    book = cur.fetchone()
    if not book or book['available'] <= 0:
        cur.close()
        conn.close()
        return redirect("/issue_book?msg=no_book")

    # Step 3: Check if member exists
    cur.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
    member = cur.fetchone()
    if not member:
        cur.close()
        conn.close()
        return redirect("/issue_book?msg=no_member")

    # Step 4: Insert the issue record
    cur.execute(
        "INSERT INTO issued_books (member_id, book_id, issue_date, due_date) VALUES (%s, %s, %s, %s)",
        (int(member_id), int(book_id), issue_date, due_date)
    )

    # Step 5: Reduce the book's available count by 1
    cur.execute(
        "UPDATE books SET available = available - 1 WHERE book_id = %s",
        (int(book_id),)
    )

    conn.commit()
    cur.close()
    conn.close()
    return redirect("/issue_book?msg=ok")


# ─────────────────────────────────────────────
# VIEW ALL ISSUED BOOKS  (GET /issued)
# ─────────────────────────────────────────────
@app.route("/issued")
def view_issued():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT i.issue_id, m.name AS member_name, b.title AS book_title,
               i.issue_date, i.due_date
        FROM issued_books i
        JOIN members m ON i.member_id = m.member_id
        JOIN books   b ON i.book_id   = b.book_id
        ORDER BY i.issue_id DESC
    """)
    issued = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("issued.html", issued=issued)


# ─────────────────────────────────────────────
# START THE APP
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
