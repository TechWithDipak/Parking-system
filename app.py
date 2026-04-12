import mysql.connector
from flask import Flask, render_template_string, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
import math
import random

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
        # Ensure Autocommit is OFF for manual Transaction Management (ACID)
        conn.autocommit = False
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
    <nav class="bg-slate-800 text-white p-4 shadow-lg sticky top-0 z-40">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold"><i class="fas fa-parking text-yellow-400 mr-2"></i>ParkingSys Pro</h1>
            {% if session.get('logged_in') %}
            <div class="flex items-center space-x-6">
                <a href="/dashboard" class="hover:text-yellow-400 transition"><i class="fas fa-table-cells mr-1"></i> Dashboard</a>
                <a href="/customers" class="hover:text-yellow-400 transition"><i class="fas fa-users mr-1"></i> Customers</a>
                <a href="/history" class="hover:text-yellow-400 transition"><i class="fas fa-history mr-1"></i> History</a>
                <a href="/reports" class="hover:text-yellow-400 transition"><i class="fas fa-chart-pie mr-1"></i> Reports</a>
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

HTML_CUSTOMERS = """
<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Add Customer Form -->
    <div class="col-span-1 bg-white p-6 rounded-xl shadow-lg h-fit border border-gray-100">
        <h3 class="text-lg font-bold mb-4 border-b pb-3 text-gray-800"><i class="fas fa-user-plus mr-2 text-blue-500"></i> Register Customer</h3>
        <form action="/customers/add" method="POST">
            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2">Customer Name</label>
                <input type="text" name="name" placeholder="John Doe" class="w-full px-3 py-2 border rounded-lg bg-gray-50" required>
            </div>
            <div class="mb-5">
                <label class="block text-gray-700 text-sm font-bold mb-2">Vehicle License Plate</label>
                <input type="text" name="vehicle_plate" placeholder="MH12AB1234" class="w-full px-3 py-2 border rounded-lg uppercase bg-gray-50" required>
            </div>
            <button type="submit" class="w-full bg-blue-600 text-white font-bold py-3 rounded-lg hover:bg-blue-700 transition shadow-md">
                Register Customer
            </button>
        </form>
    </div>

    <!-- Customer List -->
    <div class="col-span-1 lg:col-span-2 bg-white rounded-xl shadow-lg p-6 border border-gray-100">
        <h2 class="text-xl font-bold mb-4 text-gray-800 border-b pb-2"><i class="fas fa-users text-blue-500 mr-2"></i> Registered Customers Database</h2>
        <div class="overflow-x-auto max-h-[600px] overflow-y-auto">
            <table class="min-w-full bg-white border rounded-lg overflow-hidden">
                <thead class="bg-slate-800 text-white sticky top-0">
                    <tr>
                        <th class="py-3 px-4 text-left font-semibold text-sm">Customer ID</th>
                        <th class="py-3 px-4 text-left font-semibold text-sm">Name</th>
                        <th class="py-3 px-4 text-left font-semibold text-sm">Vehicle Plate</th>
                        <th class="py-3 px-4 text-left font-semibold text-sm">Registered Date</th>
                    </tr>
                </thead>
                <tbody class="text-gray-700">
                    {% for customer in customers %}
                    <tr class="border-b hover:bg-gray-50">
                        <td class="py-3 px-4 font-bold text-blue-600">{{ customer.customer_code }}</td>
                        <td class="py-3 px-4">{{ customer.name }}</td>
                        <td class="py-3 px-4 font-mono font-bold">{{ customer.vehicle_plate }}</td>
                        <td class="py-3 px-4 text-sm">{{ customer.created_at.strftime('%Y-%m-%d') if customer.created_at else '' }}</td>
                    </tr>
                    {% else %}
                    <tr><td colspan="4" class="py-4 text-center text-gray-500">No customers registered yet.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
"""

HTML_DASHBOARD = """
<div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
    <!-- Parking Operation Form (Left Panel) -->
    <div class="col-span-1 bg-white p-6 rounded-xl shadow-lg h-fit border border-gray-100 sticky top-24">
        <h3 class="text-lg font-bold mb-4 border-b pb-3 text-gray-800"><i class="fas fa-car-side mr-2 text-blue-500"></i> Check-In Vehicle</h3>
        <form action="/park" method="POST">
            
            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2 text-blue-600">Registered Customer (Optional)</label>
                <select id="customerSelect" class="w-full px-3 py-2 border border-blue-300 rounded-lg bg-blue-50 focus:ring-2 focus:ring-blue-500">
                    <option value="">-- Guest / Walk-in --</option>
                    {% for c in customers %}
                    <option value="{{ c.vehicle_plate }}">{{ c.customer_code }} - {{ c.name }}</option>
                    {% endfor %}
                </select>
                <p class="text-xs text-gray-500 mt-1">Selecting a customer auto-fills the license plate.</p>
            </div>

            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2">License Plate <span class="text-red-500">*</span></label>
                <input type="text" id="plateInput" name="plate" placeholder="e.g. MH12AB1234" class="w-full px-3 py-2 border rounded-lg uppercase bg-gray-50 font-mono transition-colors" required>
            </div>
            <div class="mb-5">
                <label class="block text-gray-700 text-sm font-bold mb-2">Assign Spot <span class="text-red-500">*</span></label>
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
            <h3 class="text-xl font-bold mb-4 text-gray-800 border-b pb-2">{{ zone }} ({{ zone_spots|selectattr('is_occupied', 'equalto', 0)|list|length }} free / {{ zone_spots|length }} total)</h3>
            
            <!-- Dense Grid for 20-25 spots -->
            <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8 gap-3">
                {% for spot in zone_spots %}
                <div class="relative p-3 rounded-xl border-2 text-center transition flex flex-col justify-between
                            {{ 'border-red-400 bg-red-50 shadow-md' if spot.is_occupied else 'border-green-400 bg-green-50' }}">
                    
                    <div class="flex justify-between items-center mb-1">
                        <span class="font-bold text-md">{{ spot.spot_number }}</span>
                        <span class="text-[10px] bg-gray-200 text-gray-700 px-1 py-0.5 rounded">{{ spot.type_name }}</span>
                    </div>
                    
                    {% if spot.is_occupied %}
                        <div class="text-red-500 my-1"><i class="fas fa-car fa-2x"></i></div>
                        <div class="text-xs font-mono font-bold bg-white border border-red-200 rounded px-1 py-1 mb-2 shadow-sm break-words">{{ spot.vehicle_plate }}</div>
                        
                        <button onclick="openCheckoutModal({{ spot.spot_id }})" class="mt-auto text-xs font-bold bg-red-600 text-white px-1 py-1.5 rounded hover:bg-red-700 w-full shadow transition transform hover:scale-105">
                            Check-Out
                        </button>
                    {% else %}
                        <div class="text-green-500 my-2"><i class="fas fa-parking fa-2x opacity-50"></i></div>
                        <span class="text-xs font-bold text-green-700 mt-auto">Available</span>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
    </div>
</div>

<!-- ========================================== -->
<!-- CHECKOUT MODAL POPUP -->
<!-- ========================================== -->
<div id="checkoutModal" class="fixed inset-0 bg-gray-900 bg-opacity-75 hidden flex justify-center items-center z-50">
    <div class="bg-white p-8 rounded-xl shadow-2xl w-full max-w-md transform transition-all scale-95 opacity-0" id="modalContent">
        <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold text-gray-800"><i class="fas fa-file-invoice-dollar text-green-500 mr-2"></i> Checkout Summary</h2>
            <button onclick="closeModal()" class="text-gray-500 hover:text-red-500"><i class="fas fa-times fa-lg"></i></button>
        </div>
        
        <div class="bg-gray-50 p-4 rounded-lg border border-gray-200 mb-6">
            <div class="flex justify-between mb-2">
                <span class="text-gray-600">Vehicle Plate:</span>
                <span id="modalPlate" class="font-bold font-mono text-lg text-gray-800"></span>
            </div>
            <div class="flex justify-between mb-2">
                <span class="text-gray-600">Spot Number:</span>
                <span id="modalSpot" class="font-bold text-gray-800"></span>
            </div>
            <div class="flex justify-between mb-4">
                <span class="text-gray-600">Duration (Hours):</span>
                <span id="modalDuration" class="font-bold text-gray-800"></span>
            </div>
            <div class="border-t border-gray-300 pt-3 flex justify-between items-center">
                <span class="text-gray-800 font-bold text-lg">Total Amount:</span>
                <span class="text-3xl font-bold text-red-600">$<span id="modalFee"></span></span>
            </div>
            <div id="modalPassNotice" class="text-green-600 text-sm font-bold text-right mt-1 hidden">
                <i class="fas fa-check-circle"></i> Active Monthly Pass Applied
            </div>
        </div>

        <form action="/exit" method="POST">
            <input type="hidden" name="spot_id" id="modalSpotId">
            <div class="mb-6">
                <label class="block text-gray-700 text-sm font-bold mb-2">Select Payment Method</label>
                <select name="payment_method" id="paymentMethod" class="w-full p-3 border rounded-lg bg-white focus:ring-2 focus:ring-blue-500" required>
                    <option value="Cash">Cash</option>
                    <option value="Card">Card / PoS</option>
                    <option value="UPI">UPI / QR Code</option>
                </select>
            </div>
            <div class="flex justify-end space-x-3">
                <button type="button" onclick="closeModal()" class="px-5 py-3 bg-gray-200 text-gray-800 font-bold rounded-lg hover:bg-gray-300 transition">Cancel</button>
                <button type="submit" class="px-5 py-3 bg-green-600 text-white font-bold rounded-lg hover:bg-green-700 transition shadow-lg flex items-center">
                    <i class="fas fa-check mr-2"></i> Confirm & Collect
                </button>
            </div>
        </form>
    </div>
</div>

<script>
    // Autofill License Plate when Customer is selected
    document.getElementById('customerSelect')?.addEventListener('change', function() {
        const plateInput = document.getElementById('plateInput');
        if(this.value) {
            plateInput.value = this.value;
            plateInput.readOnly = true;
            plateInput.classList.add('bg-blue-100', 'border-blue-400');
            plateInput.classList.remove('bg-gray-50');
        } else {
            plateInput.value = '';
            plateInput.readOnly = false;
            plateInput.classList.remove('bg-blue-100', 'border-blue-400');
            plateInput.classList.add('bg-gray-50');
        }
    });

    function openCheckoutModal(spotId) {
        // Fetch fee details from the backend API
        fetch(`/api/calculate_fee/${spotId}`)
            .then(response => response.json())
            .then(data => {
                if(data.error) {
                    alert(data.error);
                    return;
                }
                // Populate Modal Data
                document.getElementById('modalSpotId').value = spotId;
                document.getElementById('modalPlate').innerText = data.plate;
                document.getElementById('modalSpot').innerText = data.spot_number;
                document.getElementById('modalDuration').innerText = data.hours + " hr(s)";
                document.getElementById('modalFee').innerText = parseFloat(data.fee).toFixed(2);
                
                // Show/Hide Monthly Pass Notice
                const passNotice = document.getElementById('modalPassNotice');
                const paymentDropdown = document.getElementById('paymentMethod');
                
                if(data.has_pass) {
                    passNotice.classList.remove('hidden');
                    paymentDropdown.innerHTML = '<option value="Pass (Free)">Monthly Pass (Free)</option>';
                } else {
                    passNotice.classList.add('hidden');
                    paymentDropdown.innerHTML = '<option value="Cash">Cash</option><option value="Card">Card / PoS</option><option value="UPI">UPI / QR Code</option>';
                }

                // Display Modal with animation
                const modal = document.getElementById('checkoutModal');
                const content = document.getElementById('modalContent');
                modal.classList.remove('hidden');
                setTimeout(() => {
                    content.classList.remove('scale-95', 'opacity-0');
                    content.classList.add('scale-100', 'opacity-100');
                }, 10);
            });
    }

    function closeModal() {
        const modal = document.getElementById('checkoutModal');
        const content = document.getElementById('modalContent');
        content.classList.remove('scale-100', 'opacity-100');
        content.classList.add('scale-95', 'opacity-0');
        setTimeout(() => {
            modal.classList.add('hidden');
        }, 200); // Wait for transition
    }
</script>
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

HTML_REPORTS = """
<div class="bg-white rounded-xl shadow-lg p-8">
    <h2 class="text-2xl font-bold mb-6 text-gray-800"><i class="fas fa-chart-bar text-purple-500 mr-2"></i> Lock Mechanism Demonstration & Reports</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="p-6 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 class="text-xl font-bold text-blue-800 mb-4">Table-Level Locking Status</h3>
            <p class="text-gray-700 mb-4 text-sm">
                This report generated using a <code>LOCK TABLES ... READ / WRITE</code> (Table-Level Shared & Exclusive Locks) to guarantee absolute snapshot consistency across multiple tables without phantom reads.
            </p>
            <ul class="space-y-3">
                <li class="flex justify-between font-bold"><span><i class="fas fa-money-check text-green-600 mr-2"></i> Total Cash Revenue:</span> <span>${{ totals.cash|default('0.00') }}</span></li>
                <li class="flex justify-between font-bold"><span><i class="fas fa-credit-card text-blue-600 mr-2"></i> Total Card Revenue:</span> <span>${{ totals.card|default('0.00') }}</span></li>
                <li class="flex justify-between font-bold"><span><i class="fas fa-qrcode text-purple-600 mr-2"></i> Total UPI Revenue:</span> <span>${{ totals.upi|default('0.00') }}</span></li>
                <li class="flex justify-between font-bold text-xl border-t border-blue-200 pt-3 text-gray-900"><span>Grand Total:</span> <span>${{ totals.total|default('0.00') }}</span></li>
            </ul>
        </div>
        
        <div class="p-6 bg-orange-50 border border-orange-200 rounded-lg">
            <h3 class="text-xl font-bold text-orange-800 mb-4">Row-Level Locking Guide (ACID)</h3>
            <ul class="text-sm text-gray-700 space-y-4">
                <li><i class="fas fa-lock mr-2 text-red-500"></i><strong>Row-Level Exclusive Lock:</strong> Used in Check-In and Check-Out. <code>SELECT ... FOR UPDATE</code> blocks other transactions from modifying or reading the specific spot or transaction row until <code>COMMIT</code>.</li>
                <li><i class="fas fa-lock-open mr-2 text-green-500"></i><strong>Row-Level Shared Lock:</strong> Used in the Fare Calculation popup. <code>SELECT ... FOR SHARE</code> allows others to read, but prevents modifications while the rate is being calculated.</li>
            </ul>
            <div class="mt-4 text-xs font-mono bg-white p-3 border rounded">
                Example: cursor.execute("SELECT ... FOR UPDATE")<br>
                conn.start_transaction()<br>
                conn.commit() / conn.rollback()
            </div>
        </div>
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
        if not conn:
            flash('Database Connection Error. Please check your MySQL server and password.', 'error')
            full_html = HTML_BASE.replace('{% block content %}{% endblock %}', HTML_LOGIN)
            return render_template_string(full_html)

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
    if not conn:
        return "Database Connection Failed. Please ensure MySQL is running and credentials in app.py are correct.", 500

    cursor = conn.cursor(dictionary=True)
    
    # Get spots
    cursor.execute("""
        SELECT s.*, z.zone_name, v.type_name, v.hourly_rate 
        FROM parking_spots s 
        JOIN parking_zones z ON s.zone_id = z.id 
        JOIN vehicle_types v ON s.type_id = v.id
        ORDER BY z.id, s.spot_number
    """)
    spots = cursor.fetchall()

    zoned_spots = {}
    for spot in spots:
        z_name = spot['zone_name']
        if z_name not in zoned_spots:
            zoned_spots[z_name] = []
        zoned_spots[z_name].append(spot)
        
    # Get vehicle types for legend
    cursor.execute("SELECT * FROM vehicle_types")
    types = cursor.fetchall()

    # Get customers for the dropdown
    customers = []
    try:
        cursor.execute("SELECT * FROM customers ORDER BY name")
        customers = cursor.fetchall()
    except mysql.connector.Error:
        pass # Handle case where user hasn't created the customers table yet
    
    cursor.close()
    conn.close()
    
    full_template = HTML_BASE.replace('{% block content %}{% endblock %}', HTML_DASHBOARD)
    return render_template_string(full_template, spots=spots, zoned_spots=zoned_spots, types=types, customers=customers)

@app.route('/customers')
def customers_page():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        return "Database Connection Failed. Please ensure MySQL is running.", 500

    cursor = conn.cursor(dictionary=True)
    customer_list = []
    try:
        cursor.execute("SELECT * FROM customers ORDER BY created_at DESC")
        customer_list = cursor.fetchall()
    except mysql.connector.Error:
        flash("Please create the 'customers' table in your database first!", "error")

    cursor.close()
    conn.close()

    full_template = HTML_BASE.replace('{% block content %}{% endblock %}', HTML_CUSTOMERS)
    return render_template_string(full_template, customers=customer_list)

@app.route('/customers/add', methods=['POST'])
def add_customer():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    name = request.form['name']
    vehicle_plate = request.form['vehicle_plate'].upper()
    
    # Generate a random customer code (e.g. CUST-8492)
    customer_code = f"CUST-{random.randint(1000, 9999)}"
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'error')
        return redirect(url_for('customers_page'))

    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO customers (customer_code, name, vehicle_plate) VALUES (%s, %s, %s)", 
                       (customer_code, name, vehicle_plate))
        conn.commit()
        flash(f'Customer {name} registered successfully with ID: {customer_code}!', 'success')
    except mysql.connector.IntegrityError:
        conn.rollback()
        flash('Error: This Vehicle Plate is already registered to a customer.', 'error')
    except Exception as e:
        conn.rollback()
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('customers_page'))

@app.route('/park', methods=['POST'])
def park_vehicle():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    plate = request.form['plate'].upper()
    spot_id = request.form['spot_id']
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'error')
        return redirect(url_for('dashboard'))

    cursor = conn.cursor()
    
    try:
        # --- ACID: Explicitly start transaction ---
        conn.start_transaction()

        # --- CONCURRENCY CONTROL: Row-level Exclusive Lock ---
        # Prevent another operator from acquiring this exact spot simultaneously
        cursor.execute("SELECT is_occupied FROM parking_spots WHERE spot_id = %s FOR UPDATE", (spot_id,))
        spot = cursor.fetchone()
        
        if spot and spot[0]:
            conn.rollback() # ACID: Rollback on invalid state
            flash('Error: This spot was just taken by another vehicle!', 'error')
        else:
            # Atomicity: both statements execute successfully or none at all
            cursor.execute("UPDATE parking_spots SET is_occupied = TRUE, vehicle_plate = %s WHERE spot_id = %s", (plate, spot_id))
            cursor.execute("INSERT INTO transactions (vehicle_plate, spot_id, entry_time) VALUES (%s, %s, NOW())", (plate, spot_id))
            
            # --- ACID: Commit ---
            conn.commit()
            flash(f'Vehicle {plate} successfully granted entry!', 'success')
    except Exception as e:
        # --- ACID: Rollback to ensure consistency if failure occurs ---
        conn.rollback()
        flash(f'Error locking spot or processing entry: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('dashboard'))

# ==========================================
# API ENDPOINT TO CALCULATE FEE FOR POPUP
# ==========================================
@app.route('/api/calculate_fee/<int:spot_id>')
def calculate_fee(spot_id):
    if not session.get('logged_in'): return jsonify({'error': 'Unauthorized'})
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed.'})

    cursor = conn.cursor(dictionary=True)
    
    # --- CONCURRENCY CONTROL: Row-level Shared Lock (FOR SHARE) ---
    # Prevents pricing rates or transaction details from being modified while calculating
    cursor.execute("""
        SELECT t.id, t.vehicle_plate, t.entry_time, v.hourly_rate, s.spot_number
        FROM transactions t
        JOIN parking_spots s ON t.spot_id = s.spot_id
        JOIN vehicle_types v ON s.type_id = v.id
        WHERE t.spot_id = %s AND t.exit_time IS NULL LIMIT 1
        FOR SHARE
    """, (spot_id,))
    txn = cursor.fetchone()
    
    if not txn:
        return jsonify({'error': 'No active transaction found.'})
        
    # Check Monthly Pass
    cursor.execute("SELECT * FROM monthly_passes WHERE vehicle_plate = %s AND valid_until >= CURDATE()", (txn['vehicle_plate'],))
    has_pass = cursor.fetchone() is not None
    
    # Calculate
    exit_time = datetime.now()
    duration = exit_time - txn['entry_time']
    hours = math.ceil(duration.total_seconds() / 3600)
    
    fee = 0.00 if has_pass else (hours * float(txn['hourly_rate']))
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'plate': txn['vehicle_plate'],
        'spot_number': txn['spot_number'],
        'hours': hours,
        'fee': fee,
        'has_pass': has_pass
    })

@app.route('/exit', methods=['POST'])
def exit_vehicle():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    spot_id = request.form['spot_id']
    payment_method = request.form['payment_method']
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'error')
        return redirect(url_for('dashboard'))

    cursor = conn.cursor(dictionary=True)
    
    try:
        # --- ACID: Start transaction ---
        conn.start_transaction()

        # --- CONCURRENCY CONTROL: Row-level Exclusive Lock ---
        # Acquires an exclusive lock on the active transaction corresponding to the spot
        cursor.execute("""
            SELECT t.id, t.vehicle_plate, t.entry_time, v.hourly_rate
            FROM transactions t
            JOIN parking_spots s ON t.spot_id = s.spot_id
            JOIN vehicle_types v ON s.type_id = v.id
            WHERE t.spot_id = %s AND t.exit_time IS NULL LIMIT 1
            FOR UPDATE
        """, (spot_id,))
        txn = cursor.fetchone()
        
        if txn:
            plate = txn['vehicle_plate']
            entry_time = txn['entry_time']
            rate = txn['hourly_rate']
            
            cursor.execute("SELECT * FROM monthly_passes WHERE vehicle_plate = %s AND valid_until >= CURDATE()", (plate,))
            has_pass = cursor.fetchone()
            
            exit_time = datetime.now()
            duration = exit_time - entry_time
            hours = math.ceil(duration.total_seconds() / 3600)
            
            if has_pass:
                fee = 0.00
                payment_method = 'Pass (Free)'
            else:
                fee = hours * float(rate)
            
            cursor.execute("UPDATE transactions SET exit_time = %s, fee = %s WHERE id = %s", (exit_time, fee, txn['id']))
            cursor.execute("INSERT INTO payments (transaction_id, payment_method, amount) VALUES (%s, %s, %s)", (txn['id'], payment_method, fee))
            cursor.execute("UPDATE parking_spots SET is_occupied = FALSE, vehicle_plate = NULL WHERE spot_id = %s", (spot_id,))
            
            # --- ACID: COMMIT ---
            conn.commit()
            flash(f'Checkout Complete for {plate}. Total Collected: ${fee:.2f} via {payment_method}', 'success')
            
    except Exception as e:
        # --- ACID: ROLLBACK ---
        conn.rollback()
        flash(f'Transaction Error (Rolled Back): {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('dashboard'))

@app.route('/history')
def history():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        return "Database Connection Failed. Please ensure MySQL is running.", 500

    cursor = conn.cursor(dictionary=True)
    
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

@app.route('/reports')
def reports():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        return "Database Connection Failed.", 500
        
    cursor = conn.cursor(dictionary=True)
    totals = {'cash': 0, 'card': 0, 'upi': 0, 'total': 0}
    
    try:
        # --- ACID: Start transaction ---
        conn.start_transaction()
        
        # --- CONCURRENCY CONTROL: Table-level Locks ---
        # We acquire a READ lock on payments and a WRITE lock on system_audit_log
        # This demonstrates both Table-level Shared and Exclusive Locks
        cursor.execute("LOCK TABLES payments READ, system_audit_log WRITE, users READ")
        
        # Calculate secure summary (no new payments can be inserted while taking snapshot)
        cursor.execute("SELECT payment_method, SUM(amount) as total FROM payments GROUP BY payment_method")
        results = cursor.fetchall()
        
        for r in results:
            if r['payment_method'] == 'Cash': totals['cash'] = float(r['total'] or 0)
            elif 'Card' in r['payment_method']: totals['card'] = float(r['total'] or 0)
            elif 'UPI' in r['payment_method']: totals['upi'] = float(r['total'] or 0)
                
        totals['total'] = totals['cash'] + totals['card'] + totals['upi']
        
        # Demonstrate Table-level WRITE lock by inserting a reporting audit
        cursor.execute("INSERT INTO system_audit_log (action_type, details) VALUES ('REPORT_GENERATED', 'User viewed financial report')")
        
        # Remember to commit any writes while tables are locked
        conn.commit()
    except Exception as e:
        print("Error in reports:", e)
    finally:
        # ALWAYS unlock tables!
        try:
            cursor.execute("UNLOCK TABLES")
        except:
            pass
        cursor.close()
        conn.close()

    full_template = HTML_BASE.replace('{% block content %}{% endblock %}', HTML_REPORTS)
    return render_template_string(full_template, totals=totals)

if __name__ == '__main__':
    app.run(debug=True, port=5000)