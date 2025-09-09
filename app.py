from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "Pump"  

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/notes")  
    return '''
        Main page. 
        <a href='/register'>Sigh up</a> | <a href='/login'>Log in</a>
    '''


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "This email is already exsists"
        conn.close()

        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            return redirect("/notes")
        else:
            return "Invalid email or password"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/")

@app.route("/notes")
def notes():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content, image_path FROM notes WHERE user_id = ?", (session["user_id"],))
    notes = cursor.fetchall()
    conn.close()

    return render_template("notes.html", notes=notes)



@app.route("/create_note", methods=["GET", "POST"])
def create_note():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        file = request.files.get("image")
        image_path = ""

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(save_path)
            image_path = os.path.join("uploads", filename).replace("\\", "/")

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notes (user_id, title, content, image_path) VALUES (?, ?, ?, ?)",
            (session["user_id"], title, content, image_path)
        )
        conn.commit()
        conn.close()

        return redirect("/notes")

    return render_template("create_note.html")

@app.route("/delete_note/<int:note_id>", methods=["POST"])
def delete_note(note_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    
    cursor.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, session["user_id"]))
    conn.commit()
    conn.close()

    return redirect("/notes")

@app.route("/edit_note/<int:note_id>", methods=["GET", "POST"])
def edit_note(note_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

   
    cursor.execute("SELECT id, title, content, image_path FROM notes WHERE id = ? AND user_id = ?", (note_id, session["user_id"]))
    note = cursor.fetchone()

    if not note:
        conn.close()
        return "Note is not found or you do not have permission to edit it"

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        file = request.files.get("image")

        image_path = note[3]  

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(save_path)
            image_path = os.path.join("uploads", filename).replace("\\", "/")


        cursor.execute(
            "UPDATE notes SET title = ?, content = ?, image_path = ? WHERE id = ? AND user_id = ?",
            (title, content, image_path, note_id, session["user_id"])
        )
        conn.commit()
        conn.close()

        return redirect("/notes")

    conn.close()
    return render_template("edit_note.html", note=note)



import sys

if __name__ == "__main__":
    port = 5000

    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port, using 5000")

    app.run(debug=True, host="0.0.0.0", port=port)
