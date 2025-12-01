import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

app.secret_key = "super_secret_key_for_school_app" 
DB_NAME = "school.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idno INTEGER,
            name VARCHAR(100),
            course VARCHAR(50),
            level INTEGER
        )
    ''')
    conn.commit()
    conn.close()


init_db()


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
     
        idno = request.form.get('idno')
        name = request.form.get('name')
        course = request.form.get('course')
        
        if course == 'Other':
            course = request.form.get('course_other') or course
        level = request.form.get('level')

     
        if not idno or not idno.strip().isdigit():
            flash('Error: ID No must contain only digits.')
            return redirect(url_for('index'))
        idno_int = int(idno.strip())

        
        if not level or not str(level).strip().isdigit():
            flash('Error: Level must be a number.')
            return redirect(url_for('index'))
        level_int = int(str(level).strip())

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

       
        exist_id = cursor.execute("SELECT id FROM student WHERE idno = ?", (idno_int,)).fetchone()
        if exist_id:
            flash(f"Error: ID Number {idno} is already taken.")
            conn.close()
            
            return redirect(url_for('index'))

       
        exist_name = cursor.execute("SELECT id FROM student WHERE name = ? COLLATE NOCASE", (name,)).fetchone()
        if exist_name:
            flash(f"Error: The name '{name}' is already registered.")
            conn.close()
            return redirect(url_for('index'))
     

       
        cursor.execute("INSERT INTO student (idno, name, course, level) VALUES (?, ?, ?, ?)",
                       (idno_int, name, course, level_int))
        conn.commit()
        conn.close()
        
        flash("Student added successfully!")
        return redirect(url_for('view_list'))

    return render_template("add.html", student=None)


@app.route("/list")
def view_list():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    students = cursor.execute("SELECT * FROM student").fetchall()
    conn.close()
    return render_template("list.html", students=students)



@app.route('/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        idno = request.form.get('idno')
        name = request.form.get('name')
        course = request.form.get('course')
        if course == 'Other':
            course = request.form.get('course_other') or course
        level = request.form.get('level')

        
        if not idno or not idno.strip().isdigit():
            flash('Error: ID No must contain only digits.')
            conn.close()
            return redirect(url_for('edit_student', student_id=student_id))
        idno_int = int(idno.strip())

        
        if not level or not str(level).strip().isdigit():
            flash('Error: Level must be a number.')
            conn.close()
            return redirect(url_for('edit_student', student_id=student_id))
        level_int = int(str(level).strip())

       
        exist_id = cursor.execute("SELECT id FROM student WHERE idno = ? AND id != ?", (idno_int, student_id)).fetchone()
        if exist_id:
            flash(f"Error: ID Number {idno} is already taken by another student.")
            conn.close()
            return redirect(url_for('edit_student', student_id=student_id))

      
        exist_name = cursor.execute("SELECT id FROM student WHERE name = ? COLLATE NOCASE AND id != ?", (name, student_id)).fetchone()
        if exist_name:
            flash(f"Error: The name '{name}' is already used by another student.")
            conn.close()
            return redirect(url_for('edit_student', student_id=student_id))
        

        cursor.execute("UPDATE student SET idno=?, name=?, course=?, level=? WHERE id=?",
                       (idno_int, name, course, level_int, student_id))
        conn.commit()
        conn.close()
        
        flash("Student updated successfully!")
        return redirect(url_for('view_list'))

    
    student = cursor.execute("SELECT * FROM student WHERE id=?", (student_id,)).fetchone()
    conn.close()
    if not student:
        return redirect(url_for('view_list'))
    return render_template('add.html', student=student)


@app.route('/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    flash("Student deleted.")
    return redirect(url_for('view_list'))

if __name__ == "__main__":
    
    app.run(debug=True, host='192.168.161.60', port=5000)