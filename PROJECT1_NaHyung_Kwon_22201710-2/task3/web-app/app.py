from flask import Flask, render_template, request, redirect, url_for, session
import requests
import time
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

API_URL_ADD = "http://api:8080/student/add"
API_URL_ALL = "http://api:8080/student/all"

@app.route("/health")
def health_check():
    return {"status": "healthy", "service": "frontend", "timestamp": time.time()}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add", methods=["GET", "POST"])
def add_student():
    session['last_visit'] = time.time()
    
    if request.method == "POST":
        student_id = request.form["student_id"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        module_code = request.form["module_code"]

        payload = {
            "student_id": student_id,
            "first_name": first_name,
            "last_name": last_name,
            "module_code": module_code,
        }
        try:
            response = requests.post(API_URL_ADD, json=payload, timeout=5)
            if response.status_code == 200:
                session['last_action'] = 'add_success'
                return redirect(url_for("add_student"))
            else:
                session['last_action'] = 'add_error'
                return redirect(url_for("add_student"))
        except requests.exceptions.RequestException:
            session['last_action'] = 'api_error'
            return redirect(url_for("add_student"))

    last_action = session.get('last_action', '')
    session.pop('last_action', None)  # Clear after reading
    return render_template("form.html", last_action=last_action)

@app.route("/all")
def get_all_students():
    session['last_visit'] = time.time()
    try:
        response = requests.get(API_URL_ALL, timeout=5)
        if response.status_code == 200:
            students = response.json()
            return render_template("students.html", students=students)
        else:
            return f"Failed to retrieve data. Status code: {response.status_code}"
    except requests.exceptions.RequestException:
        return "API service unavailable"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")