from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash

from db import get_db_connection

register_bp = Blueprint('register', __name__)

@register_bp.route('/register', methods=['POST'])
def register():

    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    department = data.get('department')
    password = data.get('password')

    if not all([name, email, department, password]):
        return jsonify({
            "error": "All fields are required"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM Students WHERE Email = ?",
        (email,)
    )

    existing_student = cursor.fetchone()

    if existing_student:
        conn.close()

        return jsonify({
            "error": "Email already registered"
        }), 409

    hashed_password = generate_password_hash(password)

    cursor.execute("""
        INSERT INTO Students
        (Name, Email, Department, Password)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        email,
        department,
        hashed_password
    ))

    conn.commit()

    conn.close()

    return jsonify({
        "message": "Student registered successfully"
    }), 201
