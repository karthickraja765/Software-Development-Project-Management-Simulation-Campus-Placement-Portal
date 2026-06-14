from flask import Flask, jsonify
from db import get_db_connection

from auth.register import register_bp
from auth.login import login_bp

app = Flask(__name__)

app.register_blueprint(register_bp)
app.register_blueprint(login_bp)

@app.route('/health')
def health():
    return {"status": "OK", "message": "Backend is running"}

@app.route('/test-db')
def test_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Students")
    students = cursor.fetchall()

    conn.close()

    return jsonify([
        dict(student) for student in students
    ])

if __name__ == "__main__":
    app.run(debug=True)




