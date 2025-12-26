import psycopg2

# Database connection string
db_url = "postgresql://neondb_owner:npg_Jf2LGdNayZ3D@ep-late-bird-ahh0qy4j-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

try:
    # Connect to database
    connection = psycopg2.connect(db_url)
    cursor = connection.cursor()

    print("Connected to database!")

    # Check existing tables
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    print(f"\nExisting tables: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")

    # Create sample tables if none exist
    if len(tables) == 0:
        print("\nNo tables found. Creating sample tables...")

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(100),
                age INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert sample data
        cursor.execute("""
            INSERT INTO users (username, email, age) VALUES
            ('alice', 'alice@example.com', 25),
            ('bob', 'bob@example.com', 30),
            ('charlie', 'charlie@example.com', 28)
        """)

        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10, 2),
                stock INTEGER,
                category VARCHAR(50)
            )
        """)

        # Insert sample data
        cursor.execute("""
            INSERT INTO products (name, price, stock, category) VALUES
            ('Laptop', 999.99, 10, 'Electronics'),
            ('Mouse', 29.99, 50, 'Electronics'),
            ('Keyboard', 79.99, 30, 'Electronics'),
            ('Chair', 199.99, 15, 'Furniture'),
            ('Desk', 299.99, 8, 'Furniture')
        """)

        # Create tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT FALSE,
                priority INTEGER
            )
        """)

        # Insert sample data
        cursor.execute("""
            INSERT INTO tasks (title, description, completed, priority) VALUES
            ('Complete project', 'Finish the secret database game', FALSE, 1),
            ('Review code', 'Check for bugs and improvements', FALSE, 2),
            ('Write documentation', 'Document all features', FALSE, 3)
        """)

        connection.commit()
        print("Sample tables created successfully!")
        print("  - users (3 rows)")
        print("  - products (5 rows)")
        print("  - tasks (3 rows)")
    else:
        print("\nTables already exist. Database is ready!")

    cursor.close()
    connection.close()

    print("\nSetup complete! Launch the game to see your database.")

except Exception as e:
    print(f"Error: {e}")
