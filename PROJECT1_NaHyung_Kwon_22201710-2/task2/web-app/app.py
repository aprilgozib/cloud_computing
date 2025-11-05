from flask import Flask, render_template, request, redirect, url_for, session
import time
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health_check():
    return {"service": "frontend", "status": "healthy", "timestamp": time.time()}

@app.route("/add", methods=["GET", "POST"])
def add_student():
    session['last_visit'] = time.time()
    
    if request.method == "POST":
        return redirect(url_for("add_student"))

    last_action = session.get('last_action', '')
    session.pop('last_action', None)
    return render_template("form.html", last_action=last_action)

@app.route("/all")
def get_all_students():
    session['last_visit'] = time.time()
    return render_template("students.html", students=None, cache_info=None)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")