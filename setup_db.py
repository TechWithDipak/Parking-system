import mysql.connector

try:
    conn = mysql.connector.connect(host='localhost', user='root', password='Helloworld')
    cursor = conn.cursor()
    with open('schema.sql', 'r') as f:
        sql_script = f.read()
    
    # Simple split might not work for delimiter statements, but let's try. 
    # Actually, schema.sql has triggers with DELIMITER //
    # So wait, in Python, we can't easily execute multiple statements including custom delimiters without parsing carefully.
    
    print("Run `source schema.sql` in your mysql shell manually.")
except Exception as e:
    print(e)
