from flask import Flask, render_template, request, redirect, url_for, session
import requests
import time
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Simple metrics storage with endpoint tracking
metrics_data = {
    'requests': {},  # Will store {"endpoint_method": count}
    'uptime_start': time.time()
}

API_URL_ADD = "http://api:8080/student/add"
API_URL_ALL = "http://api:8080/student/all"
API_URL_ALL_WITH_CACHE = "http://api:8080/student/all/with-cache-info"
API_URL_CLEAR_CACHE = "http://api:8080/student/cache/clear"

def increment_request_count(endpoint, method="GET"):
    """Increment request count for specific endpoint and method"""
    key = f"{endpoint}_{method}"
    if key not in metrics_data['requests']:
        metrics_data['requests'][key] = 0
    metrics_data['requests'][key] += 1

@app.route("/health")
def health_check():
    return {"status": "healthy", "service": "frontend", "timestamp": time.time()}

@app.route("/metrics")
def metrics():
    """Prometheus-style metrics endpoint with proper labels"""
    uptime = time.time() - metrics_data['uptime_start']
    
    metrics_output = """# HELP request_count_total Total number of requests
# TYPE request_count_total counter
"""

    # Add request_count_total metrics with endpoint and method labels
    for key, count in metrics_data['requests'].items():
        endpoint, method = key.rsplit('_', 1)
        metrics_output += f'request_count_total{{endpoint="{endpoint}",method="{method}"}} {count}\n'
    
    # Add other metrics
    metrics_output += f"""# HELP frontend_uptime_seconds Uptime in seconds
# TYPE frontend_uptime_seconds gauge
frontend_uptime_seconds {uptime}

# HELP up Service is up
# TYPE up gauge
up 1
"""
    return metrics_output, 200, {'Content-Type': 'text/plain'}

@app.route("/")
def index():
    increment_request_count("/", "GET")
    return render_template("index.html")

@app.route("/add", methods=["GET", "POST"])
def add_student():
    increment_request_count("/add", request.method)
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
    increment_request_count("/all", "GET")
    session['last_visit'] = time.time()
    try:
        response = requests.get(API_URL_ALL_WITH_CACHE, timeout=5)
        if response.status_code == 200:
            data = response.json()
            students = data.get('data', [])
            cache_info = data.get('cache_info', {})
            return render_template("students.html", students=students, cache_info=cache_info)
        else:
            return f"Failed to retrieve data. Status code: {response.status_code}"
    except requests.exceptions.RequestException:
        return "API service unavailable"

@app.route("/clear-cache", methods=["DELETE"])
def clear_cache():
    increment_request_count("/clear-cache", "DELETE")
    try:
        response = requests.delete(API_URL_CLEAR_CACHE, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": f"API returned status {response.status_code}"}, 500
    except requests.exceptions.RequestException:
        return {"success": False, "error": "API service unavailable"}, 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")