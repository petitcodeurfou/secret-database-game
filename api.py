from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2 import sql

app = Flask(__name__)
CORS(app)  # Enable CORS for React

# Database connection string
DB_URL = "postgresql://neondb_owner:npg_Jf2LGdNayZ3D@ep-late-bird-ahh0qy4j-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

def get_db_connection():
    return psycopg2.connect(DB_URL)

@app.route('/api/tables', methods=['GET'])
def get_tables():
    """Get list of all tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify({'tables': tables})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tables/<table_name>', methods=['GET'])
def get_table_data(table_name):
    """Get all data from a specific table"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get data
        cursor.execute(sql.SQL("SELECT * FROM {} LIMIT 1000").format(
            sql.Identifier(table_name)
        ))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        # Convert to list of dicts
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))

        cursor.close()
        conn.close()
        return jsonify({
            'columns': columns,
            'data': data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tables/<table_name>/rows', methods=['POST'])
def create_row(table_name):
    """Insert a new row"""
    try:
        row_data = request.json

        # Filter out None values
        filtered_data = {k: v for k, v in row_data.items() if v is not None and v != ''}

        if not filtered_data:
            return jsonify({'error': 'No data to insert'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        columns = list(filtered_data.keys())
        values = list(filtered_data.values())

        query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING *").format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(map(sql.Identifier, columns)),
            sql.SQL(', ').join(sql.Placeholder() * len(values))
        )

        cursor.execute(query, values)
        conn.commit()

        # Get the inserted row
        new_row = cursor.fetchone()
        column_names = [desc[0] for desc in cursor.description]
        result = dict(zip(column_names, new_row))

        cursor.close()
        conn.close()

        return jsonify({'success': True, 'data': result}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tables/<table_name>/rows', methods=['PUT'])
def update_row(table_name):
    """Update an existing row"""
    try:
        data = request.json
        old_row = data.get('old')
        new_row = data.get('new')

        if not old_row or not new_row:
            return jsonify({'error': 'Missing old or new row data'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get column names
        cursor.execute(sql.SQL("SELECT * FROM {} LIMIT 0").format(
            sql.Identifier(table_name)
        ))
        columns = [desc[0] for desc in cursor.description]

        # Build SET clause
        set_items = []
        set_values = []
        for col in columns:
            if col in new_row:
                set_items.append(sql.SQL("{} = {}").format(sql.Identifier(col), sql.Placeholder()))
                set_values.append(new_row[col])

        # Build WHERE clause
        where_items = []
        where_values = []
        for col in columns:
            if col in old_row:
                where_items.append(sql.SQL("{} = {}").format(sql.Identifier(col), sql.Placeholder()))
                where_values.append(old_row[col])

        query = sql.SQL("UPDATE {} SET {} WHERE {}").format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(set_items),
            sql.SQL(' AND ').join(where_items)
        )

        cursor.execute(query, set_values + where_values)
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tables/<table_name>/rows', methods=['DELETE'])
def delete_row(table_name):
    """Delete a row"""
    try:
        row_data = request.json

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get column names
        cursor.execute(sql.SQL("SELECT * FROM {} LIMIT 0").format(
            sql.Identifier(table_name)
        ))
        columns = [desc[0] for desc in cursor.description]

        # Build WHERE clause
        where_items = []
        where_values = []
        for col in columns:
            if col in row_data:
                where_items.append(sql.SQL("{} = {}").format(sql.Identifier(col), sql.Placeholder()))
                where_values.append(row_data[col])

        query = sql.SQL("DELETE FROM {} WHERE {}").format(
            sql.Identifier(table_name),
            sql.SQL(' AND ').join(where_items)
        )

        cursor.execute(query, where_values)
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Secret Database API on http://localhost:5000")
    app.run(debug=True, port=5000)
