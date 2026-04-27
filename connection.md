# Database Connection in `app.py`

This document explains how the connection to the MySQL database is established in your `app.py` file.

## 1. Where the Connection is Configured
**Lines 11-16**
The connection credentials and details are stored in a dictionary named `db_config`:
```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Helloworld', 
    'database': 'parking_sys'
}
```

## 2. Where the Connection is Initialized
**Lines 18-26**
The actual connection is established within the `get_db_connection()` function:
```python
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        
        conn.autocommit = False
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting: {err}")
        return None
```

## 3. How It Works
1. **Library**: It uses the `mysql.connector` library (imported on line 1) to bridge the Python application with the MySQL server.
2. **Unpacking Config**: Inside `get_db_connection()`, it passes the configuration details using the dictionary unpacking syntax (`**db_config`). This automatically maps the keys (`host`, `user`, etc.) to the parameters required by `mysql.connector.connect()`.
3. **Transaction Management**: It explicitly sets `conn.autocommit = False` on line 22. This means that changes made to the database won't be saved immediately; instead, the application must manually call `conn.commit()` to save changes (or `conn.rollback()` if an error occurs). This is crucial for ACID compliance and handling concurrency safely.
4. **Error Handling**: The connection attempt is wrapped in a `try...except` block. If the server is down or credentials are wrong, it prints an error message and returns `None` instead of crashing the application.
5. **Reusability**: Because this is wrapped in a helper function, every route in `app.py` (like `/login`, `/dashboard`, `/park`, etc.) simply calls `conn = get_db_connection()` whenever it needs to query the database.
