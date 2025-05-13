import sqlite3

class Database:
    category_emojis = {
        "Food": "🍔",
        "Transport": "🚗",
        "Entertainment": "🎉",
        "Utilities": "💡",
        "Other": "🛒",
        "Shopping": "🛍️",
        "Health": "💊"
    }

    def __init__(self, db_name='sandali.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                phone TEXT,
                username TEXT,
                first_name TEXT,
                last_name TEXT
            )
        ''')
        # Expenses table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category TEXT,
                amount REAL,
                description TEXT,
                date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (telegram_id)
            )
        ''')
        # Categories table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT UNIQUE,
                FOREIGN KEY (user_id) REFERENCES users (telegram_id)
            )
        ''')
        # Investments table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS investments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                asset TEXT,
                quantity REAL,
                purchase_price REAL,
                purchase_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (telegram_id)
            )
        ''')
        self.conn.commit()

    def add_user(self, telegram_id, phone, username, first_name, last_name):
        self.cursor.execute('''
            INSERT OR REPLACE INTO users (telegram_id, phone, username, first_name, last_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (telegram_id, phone, username, first_name, last_name))
        self.conn.commit()

    def get_user(self, telegram_id):
        self.cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        return self.cursor.fetchone()

    def add_expense(self, user_id, category, amount, description, date):
        self.cursor.execute('''
            INSERT INTO expenses (user_id, category, amount, description, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, category, amount, description, date))
        self.conn.commit()

    def get_expenses(self, user_id, limit=10, offset=0):
        self.cursor.execute('''
            SELECT id, category, amount, description, date
            FROM expenses
            WHERE user_id = ?
            AND amount IS NOT NULL
            ORDER BY date DESC
            LIMIT ? OFFSET ?
        ''', (user_id, limit, offset))
        return self.cursor.fetchall()

    def delete_expense(self, user_id, expense_id):
        self.cursor.execute('''
            DELETE FROM expenses
            WHERE user_id = ? AND id = ?
        ''', (user_id, expense_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def add_category(self, user_id, name):
        try:
            self.cursor.execute('''
                INSERT INTO categories (user_id, name) VALUES (?, ?)
            ''', (user_id, name))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Category already exists

    def get_categories(self, user_id):
        self.cursor.execute('''
            SELECT name FROM categories WHERE user_id = ?
        ''', (user_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def get_spending_stats(self, user_id, start_date, end_date):
        self.cursor.execute('''
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE user_id = ? AND date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total DESC
        ''', (user_id, start_date, end_date))
        return self.cursor.fetchall()

    def add_investment(self, user_id, asset, quantity, purchase_price, purchase_date):
        self.cursor.execute('''
            INSERT INTO investments (user_id, asset, quantity, purchase_price, purchase_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, asset, quantity, purchase_price, purchase_date))
        self.conn.commit()

    def get_investments(self, user_id):
        self.cursor.execute('''
            SELECT asset, quantity, purchase_price
            FROM investments
            WHERE user_id = ?
            ORDER BY purchase_date DESC
        ''', (user_id,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

# Global database instance
db = Database()