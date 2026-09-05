from flask import Flask, render_template_string, request, redirect, session, url_for
import mysql.connector
import pywhatkit as kit

app = Flask(__name__)
app.secret_key = 'byndoor_college_secret_key'

# ಡೇಟಾಬೇಸ್ ಕನೆಕ್ಷನ್
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="college_db"
)

# HTML ವಿನ್ಯಾಸ (ಸರ್ಕಾರಿ ಪ್ರಥಮ ದರ್ಜೆ ಕಾಲೇಜು, ಬೈಂದೂರು)
BASE_HTML = """
<!DOCTYPE html>
<html lang="kn">
<head>
    <meta charset="UTF-8">
    <title>ಸರ್ಕಾರಿ ಪ್ರಥಮ ದರ್ಜೆ ಕಾಲೇಜು, ಬೈಂದೂರು</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }
        .card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); max-width: 500px; margin: auto; }
        h2, h3 { color: #1a73e8; text-align: center; }
        .form-group { margin-bottom: 15px; }
        label { display: block; font-weight: bold; margin-bottom: 5px; color: #333; }
        input, select { width: 100%; padding: 10px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
        .btn { background: #1a73e8; color: white; border: none; padding: 12px; width: 100%; border-radius: 4px; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #1557b0; }
        .logout { float: right; background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="card">
        <h3 style="margin-bottom: 5px;">ಸರ್ಕಾರಿ ಪ್ರಥಮ ದರ್ಜೆ ಕಾಲೇಜು, ಬೈಂದೂರು</h3>
        <p style="text-align: center; color: #666; font-size: 13px; margin-top: 0;">BCA ವಿಭಾಗ - ವಿದ್ಯಾರ್ಥಿ ಡೇಟಾಬೇಸ್ ಮತ್ತು ಹಾಜರಾತಿ ಸಿಸ್ಟಮ್</p>
        <hr style="border: 0; border-top: 1px solid #eee; margin: 15px 0;">
        {{ content | safe }}
    </div>
</body>
</html>
"""

# ಲಾಗಿನ್ ಪೇಜ್
LOGIN_PAGE = """
<h2>ಪೋರ್ಟಲ್ ಲಾಗಿನ್</h2>
<form action="/login" method="POST">
    <div class="form-group">
        <label>ಪಾತ್ರ (Role):</label>
        <select name="role">
            <option value="admin">ಅಡ್ಮಿನ್ (Admin)</option>
            <option value="faculty">ಅಧ್ಯಾಪಕರು (Faculty)</option>
        </select>
    </div>
    <div class="form-group">
        <label>ಯೂಸರ್ ಐಡಿ:</label>
        <input type="text" name="userid" required>
    </div>
    <div class="form-group">
        <label>ಪಾಸ್‌ವರ್ಡ್:</label>
        <input type="password" name="password" required>
    </div>
    <button type="submit" class="btn">ಪ್ರವೇಶಿಸಿ</button>
</form>
"""

# ಅಟೆಂಡೆನ್ಸ್ ಹಾಗೂ ಆಬ್ಸೆಂಟ್ ವಾಟ್ಸಾಪ್ ಪೇಜ್
FACULTY_PAGE = """
<a href="/logout" class="logout">ಲಾಗ್‌ಔಟ್</a>
<h2>ಹಾಜರಾತಿ ಮತ್ತು ವಾಟ್ಸಾಪ್ ಅಲರ್ಟ್</h2>
<form action="/submit_attendance" method="POST">
    <div class="form-group">
        <label>ವಿದ್ಯಾರ್ಥಿಯ ಹೆಸರು:</label>
        <input type="text" name="name" required>
    </div>
    <div class="form-group">
        <label>ನೋಂದಣಿ ಸಂಖ್ಯೆ (Reg No):</label>
        <input type="text" name="reg_no" required>
    </div>
    <div class="form-group">
        <label>ಪೋಷಕರ ವಾಟ್ಸಾಪ್ ನಂಬರ್ (+91 ಜೊತೆ):</label>
        <input type="text" name="phone" value="+91" required>
    </div>
    <div class="form-group">
        <label>ಹಾಜರಾತಿ ಸ್ಥಿತಿ:</label>
        <select name="status">
            <option value="Present">Present (ಹಾಜರು)</option>
            <option value="Absent">Absent (ಗೈರುಹಾಜರು)</option>
        </select>
    </div>
    <button type="submit" class="btn">ಸಬ್ಮಿಟ್ ಮಾಡಿ</button>
</form>
"""

@app.route('/')
def home():
    return render_template_string(BASE_HTML, content=LOGIN_PAGE)

@app.route('/login', methods=['POST'])
def login():
    session['user'] = request.form['userid']
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template_string(BASE_HTML, content=FACULTY_PAGE)
    return redirect(url_for('home'))

@app.route('/submit_attendance', methods=['POST'])
def submit_attendance():
    reg_no = request.form['reg_no']
    name = request.form['name']
    phone = request.form['phone']
    status = request.form['status']
    
    cursor = db.cursor()
    try:
        query = "INSERT INTO attendance (registration_no, student_name, status) VALUES (%s, %s, %s)"
        cursor.execute(query, (reg_no, name, status))
        db.commit()
    except Exception as e:
        print("DB Error:", e)

    # ವಿದ್ಯಾರ್ಥಿ Absent ಇದ್ದರೆ ಮಾತ್ರ ವಾಟ್ಸಾಪ್ ಮೆಸೇಜ್ ಕಳುಹಿಸುವುದು
    if status == 'Absent':
        message = f"ಗಮನಿಸಿ: ನಿಮ್ಮ ಮಗ/ಮಗಳು {name} (Reg No: {reg_no}) ಇಂದು ಸರ್ಕಾರಿ ಪ್ರಥಮ ದರ್ಜೆ ಕಾಲೇಜು, ಬೈಂದೂರಿಗೆ ಗೈರುಹಾಜರಾಗಿದ್ದಾರೆ (Absent)."
        try:
            kit.sendwhatmsg_instantly(phone, message, wait_time=10, tab_close=True)
            msg_status = "ವಿದ್ಯಾರ್ಥಿ ಗೈರುಹಾಜರಾಗಿದ್ದಾರೆ ಮತ್ತು ಪೋಷಕರ ವಾಟ್ಸಾಪ್‌ಗೆ ಸಂದೇಶ ಕಳುಹಿಸಲಾಗಿದೆ!"
        except Exception as e:
            msg_status = f"ಡೇಟಾ ಸೇವ್ ಆಗಿದೆ, ಆದರೆ ವಾಟ್ಸಾಪ್ ಕಳುಹಿಸುವಲ್ಲಿ ದೋಷ: {e}"
    else:
        msg_status = "ಹಾಜರಾತಿ ಯಶಸ್ವಿಯಾಗಿ ದಾಖಲಾಗಿದೆ (Present)."

    result_html = f"""
    <div style="text-align: center;">
        <h3>{msg_status}</h3>
        <br><a href="/dashboard" class="btn" style="text-decoration: none; display: inline-block; padding: 10px;">ಮತ್ತೊಂದು ಎಂಟ್ರಿ ಮಾಡಿ</a>
    </div>
    """
    return render_template_string(BASE_HTML, content=result_html)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

