from flask import Flask, jsonify, render_template, request
from db import get_db_connection

from auth.register import register_bp
from auth.login import login_bp

app = Flask(__name__)

app.register_blueprint(register_bp)
app.register_blueprint(login_bp)

@app.route('/')
def home():
    return render_template('index.html')

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

@app.route('/register-page')
def register_page():
    return render_template('register.html')

@app.route('/login-page')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
       "SELECT * FROM Students LIMIT 1"
    )

    student = cursor.fetchone()

    cursor.execute(
       "SELECT COUNT(*) AS count FROM Applications WHERE StudentID = ?",
       (student["StudentID"],)
    )

    application_count = cursor.fetchone()["count"]

    conn.close()

    return render_template(
       'dashboard.html',
       student_name=student["Name"],
       student_department=student["Department"],
       application_count=application_count
    )

@app.route('/profile')
def profile():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM Students LIMIT 1"
    )

    student = cursor.fetchone()

    conn.close()

    return render_template(
        'profile.html',
        student_name=student["Name"],
        student_email=student["Email"],
        student_department=student["Department"],
        resume_link=student["ResumeLink"]
    )

@app.route('/add-job-page')
def add_job_page():
    return render_template('add_job.html')

@app.route('/add-job', methods=['POST'])
def add_job():

    data = request.get_json()

    company = data.get('company')
    role = data.get('role')
    package = data.get('package')
    eligibility = data.get('eligibility')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO Jobs
        (Company, Role, Package, Eligibility)
        VALUES (?, ?, ?, ?)
        """,
        (company, role, package, eligibility)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Job added successfully"
    })

@app.route('/jobs')
def jobs():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM Jobs"
    )

    jobs = cursor.fetchall()

    conn.close()

    return render_template(
        'jobs.html',
        jobs=jobs
    )

@app.route('/edit-job/<int:job_id>')
def edit_job(job_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM Jobs WHERE JobID = ?",
        (job_id,)
    )

    job = cursor.fetchone()

    conn.close()

    return render_template(
        'edit_job.html',
        job=job
    )

@app.route('/update-job', methods=['POST'])
def update_job():

    data = request.get_json()

    job_id = data.get('job_id')
    company = data.get('company')
    role = data.get('role')
    package = data.get('package')
    eligibility = data.get('eligibility')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE Jobs
        SET Company = ?,
            Role = ?,
            Package = ?,
            Eligibility = ?
        WHERE JobID = ?
        """,
        (
            company,
            role,
            package,
            eligibility,
            job_id
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Job updated successfully"
    })

@app.route('/apply-job', methods=['POST'])
def apply_job():

    data = request.get_json()

    job_id = data.get('job_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM Applications
        WHERE StudentID = ?
        AND JobID = ?
        """,
        (1, job_id)
    )

    existing_application = cursor.fetchone()

    if existing_application:

        conn.close()

        return jsonify({
            "message": "You have already applied for this job"
        })

    cursor.execute(
        """
        INSERT INTO Applications
        (StudentID, JobID, Status)
        VALUES (?, ?, ?)
        """,
        (1, job_id, 'Applied')
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Application submitted successfully"
    })

@app.route('/applied-jobs')
def applied_jobs():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            Jobs.Company,
            Jobs.Role,
            Applications.Status
        FROM Applications
        JOIN Jobs
            ON Applications.JobID = Jobs.JobID
        WHERE Applications.StudentID = ?
        """,
        (1,)
    )

    applications = cursor.fetchall()

    conn.close()

    return render_template(
        'applied_jobs.html',
        applications=applications
    )

@app.route('/update-profile', methods=['POST'])
def update_profile():

    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    resume_link = data.get('resume_link')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE Students
        SET Name = ?,
            Email = ?,
            ResumeLink = ?
        WHERE StudentID = 1
        """,
        (name, email, resume_link)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Profile updated successfully"
    })

@app.route('/recruiter-register-page')
def recruiter_register_page():
    return render_template(
        'recruiter_register.html'
    )

@app.route('/recruiter-register', methods=['POST'])
def recruiter_register():

    data = request.get_json()

    company_name = data.get('company_name')
    recruiter_name = data.get('recruiter_name')
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert Company
    cursor.execute(
        """
        INSERT INTO Companies
        (CompanyName)
        VALUES (?)
        """,
        (company_name,)
    )

    company_id = cursor.lastrowid

    # Insert Recruiter
    cursor.execute(
        """
        INSERT INTO Recruiters
        (
            CompanyID,
            RecruiterName,
            Email,
            Password
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            company_id,
            recruiter_name,
            email,
            password
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Recruiter registered successfully"
    })

@app.route('/recruiter-dashboard')
def recruiter_dashboard():

    conn = get_db_connection()
    cursor = conn.cursor()

    # Company Name
    cursor.execute(
        "SELECT CompanyName FROM Companies LIMIT 1"
    )

    company = cursor.fetchone()

    # Total Jobs
    cursor.execute(
        "SELECT COUNT(*) AS count FROM Jobs"
    )

    total_jobs = cursor.fetchone()["count"]

    # Total Applications
    cursor.execute(
        "SELECT COUNT(*) AS count FROM Applications"
    )

    total_applications = cursor.fetchone()["count"]

    conn.close()

    return render_template(
        'recruiter_dashboard.html',
        company_name=company["CompanyName"],
        total_jobs=total_jobs,
        total_applications=total_applications
    )

@app.route('/applicants')
def applicants():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            Students.Name,
            Students.Email,
            Jobs.Company,
            Jobs.Role,
            Applications.Status

        FROM Applications

        JOIN Students
            ON Applications.StudentID = Students.StudentID

        JOIN Jobs
            ON Applications.JobID = Jobs.JobID
        """
    )

    applicants = cursor.fetchall()

    conn.close()

    return render_template(
        'applicants.html',
        applicants=applicants
    )

@app.route('/placement-dashboard')
def placement_dashboard():

    conn = get_db_connection()
    cursor = conn.cursor()

    # Total Students
    cursor.execute(
        "SELECT COUNT(*) AS count FROM Students"
    )
    total_students = cursor.fetchone()["count"]

    # Total Jobs
    cursor.execute(
        "SELECT COUNT(*) AS count FROM Jobs"
    )
    total_jobs = cursor.fetchone()["count"]

    # Total Applications
    cursor.execute(
        "SELECT COUNT(*) AS count FROM Applications"
    )
    total_applications = cursor.fetchone()["count"]

    # Total Recruiters
    cursor.execute(
        "SELECT COUNT(*) AS count FROM Recruiters"
    )
    total_recruiters = cursor.fetchone()["count"]

    conn.close()

    return render_template(
        'placement_dashboard.html',
        total_students=total_students,
        total_jobs=total_jobs,
        total_applications=total_applications,
        total_recruiters=total_recruiters
    )

if __name__ == "__main__":
    app.run(debug=True)




