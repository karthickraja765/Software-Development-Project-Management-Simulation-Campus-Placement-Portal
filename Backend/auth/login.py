from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash

from db import get_db_connection

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    email = data.get('email')
    password = data.get('password')
    
    print("Email Entered:", email)
    print("Password Entered:", password)

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM Students WHERE Email = ?",
        (email,)
    )

    student = cursor.fetchone()

    print("Student Found:", student)

    if not student:
        conn.close()

        return jsonify({
            "error": "Invalid email or password"
        }), 401

    print("Stored Hash:", student["Password"])
    print("Password Check Result:",
      check_password_hash(student["Password"], password))

    if not check_password_hash(
        student["Password"],
        password
    ):
        conn.close()

        return jsonify({
            "error": "Invalid email or password"
        }), 401

    conn.close()

    return jsonify({
        "message": "Login successful",
        "student": {
            "StudentID": student["StudentID"],
            "Name": student["Name"],
            "Email": student["Email"],
            "Department": student["Department"]
        }
    }), 200
