import mysql.connector
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from datetime import datetime
import math

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_session'

# ---------------------------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------------------------
# TODO: Update 'password' with your local MySQL password
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Helloworld',  # <--- CHANGE THIS
    'database': 'parking_sys'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

# ---------------------------------------------------------
# HTML TEMPLATES (Fixed: Removed inheritance tags)
# ---------------------------------------------------------
HTML_BASE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ParkingSys Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100 min-h-screen font-sans">
    <nav class="bg-slate-800 text-white p-4 shadow-lg">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-xl font-bold"><i class="fas fa-parking text-yellow-400 mr-2"></i>ParkingSys</h1>
            {% if session.get('logged_in') %}
            <div>
                <span class="mr-4 text-gray-300">Welcome, {{ session['username'] }}</span>
                <a href="/logout" class="bg-red-500 hover:bg-red-600 px-4 py-2 rounded text-sm transition">Logout</a>
            </div>
            {% endif %}
        </div>
    </nav>

    <div class="container mx-auto p-6">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="mb-4 p-4 rounded {{ 'bg-green-100 text-green-700' if category == 'success' else 'bg-red-100 text-red-700' }}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <!-- CONTENT PLACEHOLDER -->
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

HTML_LOGIN = """
<div class="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden md:max-w-md mt-10 p-8">
    <h2 class="text-2xl font-bold text-center text-gray-800 mb-6">System Login</h2>
    <form action="/login" method="POST" class="space-y-4">
        <div>
            <label class="block text-gray-700 text-sm font-bold mb-2">Username</label>
            <input type="text" name="username" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required>
        </div>
        <div>
            <label class="block text-gray-700 text-sm font-bold mb-2">Password</label>
            <input type="password" name="password" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required>
        </div>
        <button type="submit" class="w-full bg-blue-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-blue-700 transition">Sign In</button>
    </form>
</div>
"""

HTML_DASHBOARD = """
<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <!-- Stats Panel -->
    <div class="col-span-1 md:col-span-3 grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div class="bg-white p-4 rounded-lg shadow border-l-4 border-green-500">
            <div class="text-gray-500 text-sm">Available Slots</div>
            <div class="text-2xl font-bold">{{ stats.available }}</div>
        </div>
        <div class="bg-white p-4 rounded-lg shadow border-l-4 border-red-500">
            <div class="text-gray-500 text-sm">Occupied</div>
            <div class="text-2xl font-bold">{{ stats.occupied }}</div>
        </div>
        <div class="bg-white p-4 rounded-lg shadow border-l-4 border-blue-500">
            <div class="text-gray-500 text-sm">Total Capacity</div>
            <div class="text-2xl font-bold">{{ stats.total }}</div>
        </div>
    </div>

    <!-- Parking Operation Form -->
    <div class="col-span-1 bg-white p-6 rounded-lg shadow h-fit">
        <h3 class="text-lg font-bold mb-4 border-b pb-2">Entry / Park Vehicle</h3>
        <form action="/park" method="POST">
            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2">License Plate</label>
                <input type="text" name="plate" placeholder="XYZ-1234" class="w-full px-3 py-2 border rounded uppercase" required>
            </div>
            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2">Select Spot</label>
                <select name="spot_id" class="w-full px-3 py-2 border rounded">
                    {% for spot in spots if not spot.is_occupied %}
                        <option value="{{ spot.spot_id }}">{{ spot.spot_number }}</option>
                    {% else %}
                        <option disabled>No spots available</option>
                    {% endfor %}
                </select>
            </div>
            <button type="submit" class="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700 transition">
                <i class="fas fa-car mr-2"></i> Park Vehicle
            </button>
        </form>
    </div>

    <!-- Parking Grid Visualizer -->
    <div class="col-span-1 md:col-span-2 bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-bold mb-4 border-b pb-2">Live Parking Status</h3>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {% for spot in spots %}
            <div class="relative p-4 rounded-lg border-2 text-center transition 
                        {{ 'border-red-500 bg-red-50' if spot.is_occupied else 'border-green-500 bg-green-50' }}">
                <div class="font-bold text-lg mb-1">{{ spot.spot_number }}</div>
                
                {% if spot.is_occupied %}
                    <div class="text-red-600 mb-2"><i class="fas fa-car-side fa-2x"></i></div>
                    <div class="text-xs font-mono bg-white border rounded px-1 py-1">{{ spot.vehicle_plate }}</div>
                    <form action="/exit" method="POST" class="mt-2">
                        <input type="hidden" name="spot_id" value="{{ spot.spot_id }}">
                        <button type="submit" class="text-xs bg-red-600 text-white px-2 py-1 rounded hover:bg-red-700 w-full">
                            Exit & Pay
                        </button>
                    </form>
                {% else %}
                    <div class="text-green-600 mb-8"><i class="fas fa-parking fa-2x"></i></div>
                    <span class="absolute bottom-2 left-0 right-0 text-xs text-green-700">Free</span>
                {% endif %}
            </div>
            {% endfor %}
        </div>
    </div>
</div>
"""

# ---------------------------------------------------------
# FLASK ROUTES
# ---------------------------------------------------------

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user:
                session['logged_in'] = True
                session['username'] = user['username']
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid Credentials', 'error')
        else:
            flash('Database Connection Error', 'error')
            
    # Combine templates manually for string rendering
    full_html = HTML_BASE.replace('{% block content %}{% endblock %}', HTML_LOGIN)
    return render_template_string(full_html)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        return "Database Error", 500
        
    cursor = conn.cursor(dictionary=True)
    
    # Get all spots
    cursor.execute("SELECT * FROM parking_spots ORDER BY spot_number")
    spots = cursor.fetchall()
    
    # Calculate stats
    total = len(spots)
    occupied = sum(1 for spot in spots if spot['is_occupied'])
    available = total - occupied
    stats = {'total': total, 'occupied': occupied, 'available': available}
    
    cursor.close()
    conn.close()
    
    # Combine templates manually for string rendering
    full_template = HTML_BASE.replace('{% block content %}{% endblock %}', HTML_DASHBOARD)
    return render_template_string(full_template, spots=spots, stats=stats)

@app.route('/park', methods=['POST'])
def park_vehicle():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    plate = request.form['plate'].upper()
    spot_id = request.form['spot_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Update spot status
        cursor.execute("UPDATE parking_spots SET is_occupied = TRUE, vehicle_plate = %s WHERE spot_id = %s", (plate, spot_id))
        
        # 2. Log transaction entry
        cursor.execute("INSERT INTO transactions (vehicle_plate, spot_id, entry_time) VALUES (%s, %s, NOW())", (plate, spot_id))
        
        conn.commit()
        flash(f'Vehicle {plate} parked successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error parking vehicle: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('dashboard'))

@app.route('/exit', methods=['POST'])
def exit_vehicle():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    spot_id = request.form['spot_id']
    rate_per_hour = 2.00
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Find the active transaction for this spot (where exit_time is NULL)
        cursor.execute("""
            SELECT id, entry_time FROM transactions 
            WHERE spot_id = %s AND exit_time IS NULL 
            ORDER BY entry_time DESC LIMIT 1
        """, (spot_id,))
        transaction = cursor.fetchone()
        
        if transaction:
            entry_time = transaction['entry_time']
            exit_time = datetime.now()
            duration = exit_time - entry_time
            hours = math.ceil(duration.total_seconds() / 3600)
            fee = hours * rate_per_hour
            
            # 2. Update transaction
            cursor.execute("""
                UPDATE transactions 
                SET exit_time = %s, fee = %s 
                WHERE id = %s
            """, (exit_time, fee, transaction['id']))
            
            # 3. Free the spot
            cursor.execute("UPDATE parking_spots SET is_occupied = FALSE, vehicle_plate = NULL WHERE spot_id = %s", (spot_id,))
            
            conn.commit()
            flash(f'Vehicle exited. Duration: {hours}h. Fee: ${fee:.2f}', 'success')
        else:
            flash('Error: No active transaction found for this spot.', 'error')
            
    except Exception as e:
        conn.rollback()
        flash(f'Error processing exit: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)