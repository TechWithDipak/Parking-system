import mysql.connector
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from datetime import datetime
import math

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_session'

# ---------------------------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------------------------
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Helloworld', # <-- CHANGE THIS
    'database': 'parking_sys'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting: {err}")
        return None

# ---------------------------------------------------------
# HTML TEMPLATES 
# ---------------------------------------------------------
HTML_BASE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ParkingSys Pro Max</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100 min-h-screen font-sans">
    <nav class="bg-slate-800 text-white p-4 shadow-lg">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold"><i class="fas fa-parking text-yellow-400 mr-2"></i>ParkingSys Pro</h1>
            {% if session.get('logged_in') %}
            <div class="flex items-center space-x-6">
                <a href="/dashboard" class="hover:text-yellow-400 transition"><i class="fas fa-table-cells mr-1"></i> Dashboard</a>
                <a href="/history" class="hover:text-yellow-400 transition"><i class="fas fa-history mr-1"></i> History</a>
                <span class="text-gray-400 border-l pl-6 border-gray-600">User: {{ session['username'] }}</span>
                <a href="/logout" class="bg-red-500 hover:bg-red-600 px-4 py-2 rounded text-sm font-bold transition">Logout</a>
            </div>
            {% endif %}
        </div>
    </nav>

    <div class="container mx-auto p-6">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="mb-4 p-4 rounded-lg shadow {{ 'bg-green-100 text-green-700 border border-green-300' if category == 'success' else 'bg-red-100 text-red-700 border border-red-300' }}">
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
<div class="max-w-md mx-auto bg-white rounded-xl shadow-2xl overflow-hidden mt-16 p-8">
    <div class="text-center mb-8">
        <i class="fas fa-shield-alt text-4xl text-blue-600 mb-2"></i>
        <h2 class="text-2xl font-bold text-gray-800">Secure Login</h2>
    </div>
    <form action="/login" method="POST" class="space-y-5">
        <div>
            <label class="block text-gray-700 text-sm font-bold mb-2">Username</label>
            <input type="text" name="username" class="w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50" required>
        </div>
        <div>
            <label class="block text-gray-700 text-sm font-bold mb-2">Password</label>
            <input type="password" name="password" class="w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50" required>
        </div>
        <button type="submit" class="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 transition shadow-lg mt-4">Sign In</button>
    </form>
</div>
"""

HTML_DASHBOARD = """
<div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
    <!-- Parking Operation Form (Left Panel) -->
    <div class="col-span-1 bg-white p-6 rounded-xl shadow-lg h-fit border border-gray-100">
        <h3 class="text-lg font-bold mb-4 border-b pb-3 text-gray-800"><i class="fas fa-car-side mr-2 text-blue-500"></i> Check-In Vehicle</h3>
        <form action="/park" method="POST">
            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2">License Plate</label>
                <input type="text" name="plate" placeholder="e.g. MH12AB1234" class="w-full px-3 py-2 border rounded-lg uppercase bg-gray-50" required>
            </div>
            <div class="mb-5">
                <label class="block text-gray-700 text-sm font-bold mb-2">Assign Spot</label>
                <select name="spot_id" class="w-full px-3 py-2 border rounded-lg bg-gray-50">
                    {% for spot in spots if not spot.is_occupied %}
                        <option value="{{ spot.spot_id }}">{{ spot.spot_number }} ({{ spot.type_name }} - ${{ spot.hourly_rate }}/hr)</option>
                    {% else %}
                        <option disabled>Facility Full</option>
                    {% endfor %}
                </select>
            </div>
            <button type="submit" class="w-full bg-slate-800 text-white font-bold py-3 rounded-lg hover:bg-slate-700 transition shadow-md">
                Grant Entry
            </button>
        </form>
        
        <!-- Legend/Rates -->
        <div class="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-100">
            <h4 class="font-bold text-sm text-blue-800 mb-2"><i class="fas fa-info-circle mr-1"></i> Hourly Rates</h4>
            <ul class="text-sm text-blue-700 space-y-1">
                {% for t in types %}
                    <li>{{ t.type_name }}: ${{ t.hourly_rate }}/hr</li>
                {% endfor %}
            </ul>
        </div>
    </div>

    <!-- Parking Grid Visualizer (Right Panel) -->
    <div class="col-span-1 lg:col-span-3 space-y-8">
        {% for zone, zone_spots in zoned_spots.items() %}
        <div class="bg-white p-6 rounded-xl shadow-md border border-gray-100">
            <h3 class="text-xl font-bold mb-4 text-gray-800 border-b pb-2">{{ zone }}</h3>
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {% for spot in zone_spots %}
                <div class="relative p-4 rounded-xl border-2 text-center transition flex flex-col justify-between
                            {{ 'border-red-400 bg-red-50' if spot.is_occupied else 'border-green-400 bg-green-50' }}">
                    
                    <div class="flex justify-between items-center mb-2">
                        <span class="font-bold text-lg">{{ spot.spot_number }}</span>
                        <span class="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded-full">{{ spot.type_name }}</span>
                    </div>
                    
                    {% if spot.is_occupied %}
                        <div class="text-red-500 my-2"><i class="fas fa-car fa-3x"></i></div>
                        <div class="text-sm font-mono font-bold bg-white border border-red-200 rounded px-2 py-1 mb-3 shadow-sm">{{ spot.vehicle_plate }}</div>
                        
                        <form action="/exit" method="POST" class="mt-auto">
                            <input type="hidden" name="spot_id" value="{{ spot.spot_id }}">
                            <select name="payment_method" class="w-full text-xs p-1 mb-2 border rounded" required>
                                <option value="Cash">Cash</option>
                                <option value="Card">Card</option>
                                <option value="UPI">UPI</option>
                            </select>
                            <button type="submit" class="text-sm font-bold bg-red-600 text-white px-2 py-2 rounded-lg hover:bg-red-700 w-full shadow">
                                Check-Out
                            </button>
                        </form>
                    {% else %}
                        <div class="text-green-500 my-4"><i class="fas fa-parking fa-3x opacity-50"></i></div>
                        <span class="text-sm font-bold text-green-700 mt-auto">Available</span>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
    </div>
</div>
"""

HTML_HISTORY = """
<div class="bg-white rounded-xl shadow-lg p-6">
    <h2 class="text-2xl font-bold mb-6 text-gray-800"><i class="fas fa-clipboard-list text-blue-500 mr-2"></i> Transaction & Payment Logs</h2>
    <div class="overflow-x-auto">
        <table class="min-w-full bg-white border rounded-lg overflow-hidden">
            <thead class="bg-slate-800 text-white">
                <tr>
                    <th class="py-3 px-4 text-left font-semibold text-sm">Trans ID</th>
                    <th class="py-3 px-4 text-left font-semibold text-sm">Plate Number</th>
                    <th class="py-3 px-4 text-left font-semibold text-sm">Spot</th>
                    <th class="py-3 px-4 text-left font-semibold text-sm">Entry Time</th>
                    <th class="py-3 px-4 text-left font-semibold text-sm">Exit Time</th>
                    <th class="py-3 px-4 text-left font-semibold text-sm">Method</th>
                    <th class="py-3 px-4 text-left font-semibold text-sm">Fee Collected</th>
                </tr>
            </thead>
            <tbody class="text-gray-700">
                {% for log in logs %}
                <tr class="border-b hover:bg-gray-50">
                    <td class="py-3 px-4">#{{ log.id }}</td>
                    <td class="py-3 px-4 font-mono font-bold">{{ log.vehicle_plate }}</td>
                    <td class="py-3 px-4">{{ log.spot_number }}</td>
                    <td class="py-3 px-4 text-sm">{{ log.entry_time }}</td>
                    <td class="py-3 px-4 text-sm">{{ log.exit_time or 'Active' }}</td>
                    <td class="py-3 px-4">
                        {% if log.payment_method %}
                            <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">{{ log.payment_method }}</span>
                        {% else %}
                            -
                        {% endif %}
                    </td>
                    <td class="py-3 px-4 font-bold {% if log.fee > 0 %}text-red-600{% else %}text-green-600{% endif %}">
                        ${{ "%.2f"|format(log.fee) if log.fee != None else '0.00' }}
                    </td>
                </tr>
                {% else %}
                <tr><td colspan="7" class="py-4 text-center text-gray-500">No transactions found.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
"""

# ---------------------------------------------------------
# ROUTES
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
            
    full_html = HTML_BASE.replace('{% block content %}{% endblock %}', HTML_LOGIN)
    return render_template_string(full_html)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch spots with their zone and vehicle type data (JOINing tables)
    cursor.execute("""
        SELECT s.*, z.zone_name, v.type_name, v.hourly_rate 
        FROM parking_spots s 
        JOIN parking_zones z ON s.zone_id = z.id 
        JOIN vehicle_types v ON s.type_id = v.id
        ORDER BY z.id, s.spot_number
    """)
    spots = cursor.fetchall()

    # Group spots by zone for the UI
    zoned_spots = {}
    for spot in spots:
        z_name = spot['zone_name']
        if z_name not in zoned_spots:
            zoned_spots[z_name] = []
        zoned_spots[z_name].append(spot)
        
    # Fetch vehicle types for the legend
    cursor.execute("SELECT * FROM vehicle_types")
    types = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    full_template = HTML_BASE.replace('{% block content %}{% endblock %}', HTML_DASHBOARD)
    return render_template_string(full_template, spots=spots, zoned_spots=zoned_spots, types=types)

@app.route('/park', methods=['POST'])
def park_vehicle():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    plate = request.form['plate'].upper()
    spot_id = request.form['spot_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE parking_spots SET is_occupied = TRUE, vehicle_plate = %s WHERE spot_id = %s", (plate, spot_id))
        cursor.execute("INSERT INTO transactions (vehicle_plate, spot_id, entry_time) VALUES (%s, %s, NOW())", (plate, spot_id))
        conn.commit()
        flash(f'Vehicle {plate} successfully granted entry!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('dashboard'))

@app.route('/exit', methods=['POST'])
def exit_vehicle():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    spot_id = request.form['spot_id']
    payment_method = request.form['payment_method']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Get Active Transaction & Spot Details
        cursor.execute("""
            SELECT t.id, t.vehicle_plate, t.entry_time, v.hourly_rate
            FROM transactions t
            JOIN parking_spots s ON t.spot_id = s.spot_id
            JOIN vehicle_types v ON s.type_id = v.id
            WHERE t.spot_id = %s AND t.exit_time IS NULL LIMIT 1
        """, (spot_id,))
        txn = cursor.fetchone()
        
        if txn:
            plate = txn['vehicle_plate']
            entry_time = txn['entry_time']
            rate = txn['hourly_rate']
            
            # 2. Check for active Monthly Pass
            cursor.execute("SELECT * FROM monthly_passes WHERE vehicle_plate = %s AND valid_until >= CURDATE()", (plate,))
            has_pass = cursor.fetchone()
            
            # 3. Calculate Fee
            exit_time = datetime.now()
            duration = exit_time - entry_time
            hours = math.ceil(duration.total_seconds() / 3600)
            
            if has_pass:
                fee = 0.00
                payment_method = 'Pass (Free)'
            else:
                fee = hours * float(rate)
            
            # 4. Update Transaction
            cursor.execute("UPDATE transactions SET exit_time = %s, fee = %s WHERE id = %s", (exit_time, fee, txn['id']))
            
            # 5. Record Payment Log
            cursor.execute("INSERT INTO payments (transaction_id, payment_method, amount) VALUES (%s, %s, %s)", 
                          (txn['id'], payment_method, fee))
            
            # 6. Free the Spot
            cursor.execute("UPDATE parking_spots SET is_occupied = FALSE, vehicle_plate = NULL WHERE spot_id = %s", (spot_id,))
            
            conn.commit()
            
            msg = f'Checkout Complete for {plate}. Duration: {hours}hr. Total Fee: ${fee:.2f} ({payment_method})'
            flash(msg, 'success')
            
    except Exception as e:
        conn.rollback()
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('dashboard'))

@app.route('/history')
def history():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Join Transactions, Spots, and Payments to get a full view
    cursor.execute("""
        SELECT t.id, t.vehicle_plate, t.entry_time, t.exit_time, t.fee,
               s.spot_number, p.payment_method
        FROM transactions t
        JOIN parking_spots s ON t.spot_id = s.spot_id
        LEFT JOIN payments p ON t.id = p.transaction_id
        ORDER BY t.entry_time DESC LIMIT 50
    """)
    logs = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    full_template = HTML_BASE.replace('{% block content %}{% endblock %}', HTML_HISTORY)
    return render_template_string(full_template, logs=logs)

if __name__ == '__main__':
    app.run(debug=True, port=5000)