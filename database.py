import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path: str = "bot_database.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dictionary-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        is_premium BOOLEAN DEFAULT FALSE,
                        subscription_date TEXT,
                        last_active TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Signals table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS signals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        direction TEXT NOT NULL,
                        strength REAL NOT NULL,
                        entry_price REAL NOT NULL,
                        stop_loss REAL NOT NULL,
                        take_profit REAL NOT NULL,
                        position_size REAL NOT NULL,
                        risk_reward_ratio REAL NOT NULL,
                        is_simulated BOOLEAN DEFAULT FALSE,
                        factors TEXT,
                        smc_analysis TEXT,
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # User interactions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        action TEXT NOT NULL,
                        symbol TEXT,
                        details TEXT,
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Bot settings table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bot_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                logging.info("Database initialized successfully")
                
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Add or update user in database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if user exists
                cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
                exists = cursor.fetchone()
                
                if exists:
                    # Update last active
                    cursor.execute('''
                        UPDATE users 
                        SET last_active = ?, username = ?, first_name = ?, last_name = ?
                        WHERE user_id = ?
                    ''', (datetime.now().isoformat(), username, first_name, last_name, user_id))
                else:
                    # Insert new user
                    cursor.execute('''
                        INSERT INTO users (user_id, username, first_name, last_name, last_active)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (user_id, username, first_name, last_name, datetime.now().isoformat()))
                
                conn.commit()
                logging.info(f"User {user_id} added/updated in database")
                
        except Exception as e:
            logging.error(f"Error adding user {user_id}: {e}")
    
    def log_interaction(self, user_id: int, action: str, symbol: str = None, details: str = None):
        """Log user interaction"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_interactions (user_id, action, symbol, details)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, action, symbol, details))
                conn.commit()
                
        except Exception as e:
            logging.error(f"Error logging interaction: {e}")
    
    def save_signal(self, signal: Dict):
        """Save signal to database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO signals (
                        symbol, direction, strength, entry_price, stop_loss, 
                        take_profit, position_size, risk_reward_ratio, is_simulated,
                        factors, smc_analysis
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    signal['symbol'],
                    signal['direction'],
                    signal['strength'],
                    signal['entry_price'],
                    signal['stop_loss'],
                    signal['take_profit'],
                    signal['position_size'],
                    signal['risk_reward_ratio'],
                    signal['is_simulated'],
                    str(signal.get('factors', {})),
                    str(signal.get('smc_analysis', {}))
                ))
                conn.commit()
                logging.info(f"Signal saved for {signal['symbol']}")
                
        except Exception as e:
            logging.error(f"Error saving signal: {e}")
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get user info
                cursor.execute('''
                    SELECT * FROM users WHERE user_id = ?
                ''', (user_id,))
                user = cursor.fetchone()
                
                if not user:
                    return {}
                
                # Get interaction count
                cursor.execute('''
                    SELECT COUNT(*) as count FROM user_interactions WHERE user_id = ?
                ''', (user_id,))
                interaction_count = cursor.fetchone()['count']
                
                return {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'is_premium': bool(user['is_premium']),
                    'created_at': user['created_at'],
                    'last_active': user['last_active'],
                    'interaction_count': interaction_count
                }
                
        except Exception as e:
            logging.error(f"Error getting user stats: {e}")
            return {}
    
    def get_recent_signals(self, limit: int = 10) -> List[Dict]:
        """Get recent signals"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM signals 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                
                signals = []
                for row in cursor.fetchall():
                    signals.append(dict(row))
                
                return signals
                
        except Exception as e:
            logging.error(f"Error getting recent signals: {e}")
            return []
    
    def get_signal_stats(self) -> Dict:
        """Get signal statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Total signals
                cursor.execute("SELECT COUNT(*) as count FROM signals")
                total_signals = cursor.fetchone()['count']
                
                # Simulated vs live
                cursor.execute('''
                    SELECT is_simulated, COUNT(*) as count 
                    FROM signals 
                    GROUP BY is_simulated
                ''')
                simulation_stats = {row['is_simulated']: row['count'] for row in cursor.fetchall()}
                
                # Average strength
                cursor.execute("SELECT AVG(strength) as avg_strength FROM signals")
                avg_strength = cursor.fetchone()['avg_strength'] or 0
                
                # Direction distribution
                cursor.execute('''
                    SELECT direction, COUNT(*) as count 
                    FROM signals 
                    GROUP BY direction
                ''')
                direction_stats = {row['direction']: row['count'] for row in cursor.fetchall()}
                
                return {
                    'total_signals': total_signals,
                    'simulated_signals': simulation_stats.get(1, 0),
                    'live_signals': simulation_stats.get(0, 0),
                    'average_strength': round(avg_strength, 2),
                    'direction_distribution': direction_stats
                }
                
        except Exception as e:
            logging.error(f"Error getting signal stats: {e}")
            return {}
    
    def set_setting(self, key: str, value: str):
        """Set bot setting"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO bot_settings (key, value, updated_at)
                    VALUES (?, ?, ?)
                ''', (key, value, datetime.now().isoformat()))
                conn.commit()
                
        except Exception as e:
            logging.error(f"Error setting {key}: {e}")
    
    def get_setting(self, key: str, default: str = None) -> str:
        """Get bot setting"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM bot_settings WHERE key = ?", (key,))
                result = cursor.fetchone()
                return result['value'] if result else default
                
        except Exception as e:
            logging.error(f"Error getting {key}: {e}")
            return default
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old data"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete old interactions
                cursor.execute('''
                    DELETE FROM user_interactions 
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days))
                
                # Delete old signals
                cursor.execute('''
                    DELETE FROM signals 
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days))
                
                conn.commit()
                logging.info(f"Cleaned up data older than {days} days")
                
        except Exception as e:
            logging.error(f"Error cleaning up old data: {e}")

# Global database instance
db_manager = DatabaseManager()
