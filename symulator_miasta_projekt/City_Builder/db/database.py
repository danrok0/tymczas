import sqlite3

class Database:
    def __init__(self, db_name="city_builder.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_state (
                id INTEGER PRIMARY KEY,
                population INTEGER,
                money INTEGER,
                satisfaction INTEGER,
                resources TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY,
                turn INTEGER,
                population INTEGER,
                money INTEGER,
                satisfaction INTEGER,
                resources TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER
            )
        ''')

        self.conn.commit()

    def save_game_state(self, population, money, satisfaction, resources):
        self.cursor.execute('''
            INSERT INTO game_state (population, money, satisfaction, resources)
            VALUES (?, ?, ?, ?)
        ''', (population, money, satisfaction, resources))
        self.conn.commit()

    def load_game_state(self):
        self.cursor.execute('SELECT * FROM game_state ORDER BY id DESC LIMIT 1')
        return self.cursor.fetchone()

    def save_history(self, turn, population, money, satisfaction, resources):
        self.cursor.execute('''
            INSERT INTO history (turn, population, money, satisfaction, resources)
            VALUES (?, ?, ?, ?, ?)
        ''', (turn, population, money, satisfaction, resources))
        self.conn.commit()

    def load_history(self):
        self.cursor.execute('SELECT * FROM history ORDER BY turn')
        return self.cursor.fetchall()

    def save_statistics(self, name, value):
        self.cursor.execute('''
            INSERT INTO statistics (name, value)
            VALUES (?, ?)
        ''', (name, value))
        self.conn.commit()

    def load_statistics(self):
        self.cursor.execute('SELECT * FROM statistics')
        return self.cursor.fetchall()

    def close(self):
        self.conn.close() 