import sqlite3
import json
from pathlib import Path

def init_simple_database():
    """Простая инициализация базы данных"""
    
    # Создаем папку для данных
    Path('data').mkdir(exist_ok=True)
    
    # Подключаемся к базе данных
    conn = sqlite3.connect('data/bot_constructor.db')
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        username VARCHAR(100),
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        photo_url TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Таблица ботов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_bots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER NOT NULL,
        bot_token VARCHAR(100) UNIQUE NOT NULL,
        bot_username VARCHAR(100),
        bot_name VARCHAR(100) NOT NULL,
        commands TEXT DEFAULT '[]',
        welcome_message TEXT DEFAULT 'Добро пожаловать!',
        settings TEXT DEFAULT '{}',
        is_active BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (owner_id) REFERENCES users (id)
    )
    ''')
    
    # Таблица статистики
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bot_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bot_id INTEGER NOT NULL,
        date DATE DEFAULT CURRENT_DATE,
        messages_processed INTEGER DEFAULT 0,
        commands_executed INTEGER DEFAULT 0,
        users_count INTEGER DEFAULT 0,
        FOREIGN KEY (bot_id) REFERENCES user_bots (id)
    )
    ''')
    
    # Таблица плагинов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS plugins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) UNIQUE NOT NULL,
        description TEXT,
        version VARCHAR(20) DEFAULT '1.0.0',
        is_active BOOLEAN DEFAULT 0
    )
    ''')
    
    # Добавляем тестовые данные
    try:
        # Тестовый пользователь
        cursor.execute('''
        INSERT OR IGNORE INTO users (telegram_id, username, first_name, last_name) 
        VALUES (?, ?, ?, ?)
        ''', (123456, 'test_user', 'Тест', 'Пользователь'))
        
        # Получаем ID пользователя
        cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (123456,))
        user_id = cursor.fetchone()[0]
        
        # Тестовый бот
        test_commands = json.dumps([
            {'name': 'start', 'response': 'Добро пожаловать в тестового бота!'},
            {'name': 'help', 'response': 'Это помощь по тестовому боту'},
            {'name': 'info', 'response': 'Информация о тестовом боте'}
        ], ensure_ascii=False)
        
        cursor.execute('''
        INSERT OR IGNORE INTO user_bots 
        (owner_id, bot_token, bot_username, bot_name, commands, welcome_message, is_active) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, '123456789:TESTBOTtoken123456789', 'test_bot', 
              'Тестовый бот', test_commands, 'Привет! Я тестовый бот.', 1))
        
        # Тестовые плагины
        cursor.execute('''
        INSERT OR IGNORE INTO plugins (name, description, is_active) 
        VALUES 
        ('weather', 'Погодный плагин', 1),
        ('payments', 'Платежная система', 1),
        ('notifications', 'Система уведомлений', 0)
        ''')
        
        conn.commit()
        print("✅ База данных успешно инициализирована!")
        
    except Exception as e:
        print(f"❌ Ошибка при добавлении тестовых данных: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    init_simple_database()