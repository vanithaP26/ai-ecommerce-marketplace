import os
import time
import sqlite3
import re
from config import Config

class DatabaseManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.db_type = Config.DB_TYPE
        self.conn = None
        self.cache = {}  # Format: {query_key: (expiry_timestamp, result_data)}
        self.cache_ttl = 60  # Cache TTL in seconds (1 minute)
        
        self._establish_connection()
        self._initialize_database()
        self._initialized = True

    def _establish_connection(self):
        """Attempts to establish MySQL connection. Falls back to SQLite if fails or configured."""
        if self.db_type == 'mysql':
            try:
                import mysql.connector
                self.conn = mysql.connector.connect(
                    host=Config.MYSQL_HOST,
                    user=Config.MYSQL_USER,
                    password=Config.MYSQL_PASSWORD,
                    database=Config.MYSQL_DB
                )
                print("[DATABASE] Connected successfully to MySQL database.")
                return
            except Exception as e:
                print(f"[DATABASE WARNING] MySQL connection failed: {e}. Falling back to SQLite.")
                self.db_type = 'sqlite'
        
        # SQLite Connection
        try:
            self.conn = sqlite3.connect(Config.SQLITE_DB, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            # Enable Foreign Keys in SQLite
            self.conn.execute("PRAGMA foreign_keys = ON;")
            print(f"[DATABASE] Connected successfully to SQLite database at: {Config.SQLITE_DB}")
        except Exception as e:
            print(f"[DATABASE ERROR] Failed to connect to SQLite: {e}")

    def _initialize_database(self):
        """Initializes tables and seeds initial data using database.sql."""
        try:
            # Check if users table already exists
            cursor = self.conn.cursor()
            if self.db_type == 'mysql':
                cursor.execute("SHOW TABLES LIKE 'users'")
                exists = cursor.fetchone()
            else:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
                exists = cursor.fetchone()
            
            if exists:
                try:
                    cursor.execute("SELECT COUNT(*) as count FROM categories")
                    cat_count = cursor.fetchone()
                    count_val = cat_count['count'] if isinstance(cat_count, dict) else (cat_count[0] if cat_count else 0)
                    if count_val > 0:
                        return
                except Exception:
                    pass
            
            print("[DATABASE] Initializing schema...")
            sql_file_path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'database.sql')
            if not os.path.exists(sql_file_path):
                print(f"[DATABASE ERROR] Schema file database.sql not found at {sql_file_path}")
                return
            
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                schema_content = f.read()

            if self.db_type == 'mysql':
                # Run script on MySQL
                # mysql-connector's execute doesn't support multiple queries by default unless using multi=True
                statements = schema_content.split(';')
                for stmt in statements:
                    stmt = stmt.strip()
                    if stmt and not stmt.startswith('--'):
                        cursor.execute(stmt)
                self.conn.commit()
            else:
                # Convert MySQL DDL to SQLite DDL dynamically
                sqlite_schema = self._convert_mysql_to_sqlite(schema_content)
                # sqlite3 supports executescript
                self.conn.executescript(sqlite_schema)
                self.conn.commit()
                
            print("[DATABASE] Database initialization completed successfully.")
        except Exception as e:
            print(f"[DATABASE ERROR] Failed to initialize database: {e}")

    def _convert_mysql_to_sqlite(self, sql):
        """Converts basic MySQL statements into SQLite-compatible commands."""
        # 1. Disable MySQL checks
        sql = sql.replace("SET FOREIGN_KEY_CHECKS = 0;", "")
        sql = sql.replace("SET FOREIGN_KEY_CHECKS = 1;", "")
        
        # 2. Convert autoincrement syntax
        # SQLite requires INTEGER PRIMARY KEY AUTOINCREMENT (no INT, and must be PRIMARY KEY on the same column definition)
        sql = re.sub(
            r'(\w+)\s+INT\s+AUTO_INCREMENT\s+PRIMARY\s+KEY', 
            r'\1 INTEGER PRIMARY KEY AUTOINCREMENT', 
            sql, 
            flags=re.IGNORECASE
        )
        
        # 3. Clean up Engine and Charset options
        sql = re.sub(
            r'ENGINE\s*=\s*\w+\s+(DEFAULT\s+CHARSET\s*=\s*\w+\s*(COLLATE\s*=\s*[\w_]+)?)?', 
            '', 
            sql, 
            flags=re.IGNORECASE
        )
        
        # 4. Remove inline index definitions (e.g., INDEX idx_name (col), UNIQUE KEY unique_name (col1, col2))
        # SQLite does not support inline INDEX inside CREATE TABLE.
        # We need to extract these and generate separate CREATE INDEX statements.
        lines = sql.split('\n')
        cleaned_lines = []
        indexes_to_create = []
        current_table = None
        
        for line in lines:
            # Capture table name
            table_match = re.match(r'^\s*CREATE\s+TABLE\s+(\w+)', line, re.IGNORECASE)
            if table_match:
                current_table = table_match.group(1)
            
            line_strip = line.strip()
            # Match: INDEX idx_name (col1, col2)
            idx_match = re.match(r'^INDEX\s+(\w+)\s*\(([^)]+)\),?$', line_strip, re.IGNORECASE)
            # Match: UNIQUE KEY idx_name (col1, col2)
            unique_match = re.match(r'^UNIQUE\s+KEY\s+(\w+)\s*\(([^)]+)\),?$', line_strip, re.IGNORECASE)
            
            if idx_match and current_table:
                idx_name, cols = idx_match.group(1), idx_match.group(2)
                indexes_to_create.append(f"CREATE INDEX {idx_name} ON {current_table} ({cols});")
                # Remove trailing comma if this was the last column in the table list
                if cleaned_lines and cleaned_lines[-1].endswith(','):
                    pass
                continue
            elif unique_match and current_table:
                idx_name, cols = unique_match.group(1), unique_match.group(2)
                indexes_to_create.append(f"CREATE UNIQUE INDEX {idx_name} ON {current_table} ({cols});")
                continue
            
            cleaned_lines.append(line)
        
        sql = '\n'.join(cleaned_lines)
        
        # Add generated CREATE INDEX statements
        sql += "\n\n" + "\n".join(indexes_to_create)
        
        # 5. Fix SQLites inability to drop column or do complex checks/types in some versions
        # Remove trailing comma inside table columns definitions if we stripped the index line
        # This regex cleans up trailing commas right before table closing parenthesis
        sql = re.sub(r',\s*\n\s*\)', '\n)', sql)
        
        # 6. Replace DECIMAL with REAL or NUMERIC for SQLite
        sql = re.sub(r'DECIMAL\(\d+,\d+\)', 'NUMERIC', sql, flags=re.IGNORECASE)
        
        # 7. Strip ON UPDATE CURRENT_TIMESTAMP for SQLite
        sql = re.sub(r'ON\s+UPDATE\s+CURRENT_TIMESTAMP', '', sql, flags=re.IGNORECASE)
        
        return sql

    def _translate_sql(self, sql):
        """Translates MySQL syntax (e.g. placeholder %s) to SQLite syntax (?) if needed."""
        if self.db_type == 'sqlite':
            # Substitute %s with ? for parameter binding
            # Use regex to replace %s but avoid replacing actual string formats or % characters
            # In database calls we use %s for parameterized values
            return sql.replace('%s', '?')
        return sql

    def execute_query(self, sql, params=None, cache=False):
        """
        Executes a SELECT query. Implements query cache if cache=True.
        Returns a list of dicts.
        """
        sql_translated = self._translate_sql(sql)
        params_tuple = tuple(params) if params else ()
        cache_key = (sql_translated, params_tuple)
        
        # Check cache
        if cache:
            now = time.time()
            if cache_key in self.cache:
                expiry, cached_result = self.cache[cache_key]
                if now < expiry:
                    return cached_result
                else:
                    del self.cache[cache_key]

        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(sql_translated, params)
            else:
                cursor.execute(sql_translated)
            
            # Fetch results
            if self.db_type == 'mysql':
                # For MySQL, return records as dicts
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                # For SQLite, rows are sqlite3.Row, convert to dict
                results = [dict(row) for row in cursor.fetchall()]
                
            cursor.close()
            
            # Write to cache
            if cache:
                self.cache[cache_key] = (time.time() + self.cache_ttl, results)
                
            return results
        except Exception as e:
            print(f"[DATABASE QUERY ERROR] Query: {sql_translated}\nError: {e}")
            return []

    def execute_non_query(self, sql, params=None):
        """
        Executes INSERT, UPDATE, DELETE queries.
        Invalidates query cache.
        Returns rowcount or lastrowid.
        """
        sql_translated = self._translate_sql(sql)
        # Invalidate cache since database is modified
        self.cache.clear()
        
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(sql_translated, params)
            else:
                cursor.execute(sql_translated)
            
            self.conn.commit()
            
            # Return last row ID for INSERTs
            last_id = cursor.lastrowid
            row_count = cursor.rowcount
            cursor.close()
            
            if sql_translated.strip().upper().startswith('INSERT'):
                return last_id
            return row_count
        except Exception as e:
            print(f"[DATABASE EXECUTE ERROR] Query: {sql_translated}\nError: {e}")
            if self.conn:
                self.conn.rollback()
            raise e

    def close(self):
        if self.conn:
            self.conn.close()
            print("[DATABASE] Connection closed.")
