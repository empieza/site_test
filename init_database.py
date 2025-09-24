import sqlite3
import json
from pathlib import Path

def init_database():
    """Инициализация базы данных с совместимой структурой для SQLiteStudio"""
    
    # Создаем папку для базы данных
    Path('data').mkdir(exist_ok=True)
    
    # Подключаемся к базе данных
    conn = sqlite3.connect('data/bot_constructor.db')
    cursor = conn.cursor()
    
    # Таблица пользователей (расширяем базовую структуру)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        username VARCHAR(100),
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Таблица ботов с улучшенной структурой
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_bots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER NOT NULL,
        bot_token VARCHAR(100) UNIQUE NOT NULL,
        bot_username VARCHAR(100),
        bot_name VARCHAR(100) NOT NULL,
        commands JSON DEFAULT '[]',
        welcome_message TEXT DEFAULT 'Добро пожаловать!',
        settings JSON DEFAULT '{}',
        is_active BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (owner_id) REFERENCES users (id)
    )
    ''')
    
    # Таблица статистики ботов
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
        is_active BOOLEAN DEFAULT 0,
        settings JSON DEFAULT '{}'
    )
    ''')
    
    # Таблица связей ботов с плагинами
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bot_plugins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bot_id INTEGER NOT NULL,
        plugin_id INTEGER NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        settings JSON DEFAULT '{}',
        FOREIGN KEY (bot_id) REFERENCES user_bots (id),
        FOREIGN KEY (plugin_id) REFERENCES plugins (id),
        UNIQUE(bot_id, plugin_id)
    )
    ''')
    
    # Таблица логов (для мониторинга)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bot_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bot_id INTEGER NOT NULL,
        level VARCHAR(20) DEFAULT 'INFO',
        message TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (bot_id) REFERENCES user_bots (id)
    )
    ''')
    
    # Вставляем тестовые данные для демонстрации в SQLiteStudio
    try:
        # Тестовый пользователь
        cursor.execute('''
        INSERT OR IGNORE INTO users (telegram_id, username, first_name, last_name) 
        VALUES (?, ?, ?, ?)
        ''', (123456789, 'test_user', 'Тест', 'Пользователь'))
        
        # Тестовый бот
        test_commands = json.dumps([
            {'name': 'start', 'response': 'Добро пожаловать!'},
            {'name': 'help', 'response': 'Помощь по боту'},
            {'name': 'info', 'response': 'Информация о боте'}
        ], ensure_ascii=False)
        
        cursor.execute('''
        INSERT OR IGNORE INTO user_bots 
        (owner_id, bot_token, bot_username, bot_name, commands, welcome_message, is_active) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (1, '123456789:ABCdefGHIjklMNOpqrSTUvwxYZ', 'test_bot', 
              'Тестовый бот', test_commands, 'Привет! Я тестовый бот.', 1))
        
        # Тестовые плагины
        cursor.execute('''
        INSERT OR IGNORE INTO plugins (name, description, is_active) 
        VALUES 
        ('weather', 'Погодный плагин', 1),
        ('payments', 'Платежная система', 1),
        ('notifications', 'Система уведомлений', 0)
        ''')
        
        # Тестовая статистика
        cursor.execute('''
        INSERT OR IGNORE INTO bot_stats 
        (bot_id, messages_processed, commands_executed, users_count) 
        VALUES (?, ?, ?, ?)
        ''', (1, 1500, 450, 125))
        
        conn.commit()
        print("✅ База данных успешно инициализирована!")
        print("📊 Таблицы созданы:")
        print("   - users (пользователи)")
        print("   - user_bots (боты)")
        print("   - bot_stats (статистика)")
        print("   - plugins (плагины)")
        print("   - bot_plugins (связи ботов с плагинами)")
        print("   - bot_logs (логи)")
        print("🎯 Тестовые данные добавлены")
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка при добавлении тестовых данных: {e}")
    
    finally:
        conn.close()

def create_views():
    """Создание представлений для удобного просмотра в SQLiteStudio"""
    
    conn = sqlite3.connect('data/bot_constructor.db')
    cursor = conn.cursor()
    
    # Представление для просмотра ботов с информацией о владельце
    cursor.execute('''
    CREATE VIEW IF NOT EXISTS v_bots_with_owners AS
    SELECT 
        ub.id,
        ub.bot_name,
        ub.bot_username,
        ub.is_active,
        u.username as owner_username,
        u.first_name as owner_first_name,
        ub.created_at,
        json_array_length(ub.commands) as commands_count
    FROM user_bots ub
    LEFT JOIN users u ON ub.owner_id = u.id
    ''')
    
    # Представление для статистики ботов
    cursor.execute('''
    CREATE VIEW IF NOT EXISTS v_bots_stats AS
    SELECT 
        ub.bot_name,
        bs.date,
        bs.messages_processed,
        bs.commands_executed,
        bs.users_count,
        (bs.messages_processed * 1.0 / bs.users_count) as avg_messages_per_user
    FROM bot_stats bs
    JOIN user_bots ub ON bs.bot_id = ub.id
    ''')
    
    # Представление для активных плагинов
    cursor.execute('''
    CREATE VIEW IF NOT EXISTS v_active_plugins AS
    SELECT 
        p.name,
        p.description,
        p.version,
        COUNT(bp.bot_id) as active_bots_count
    FROM plugins p
    LEFT JOIN bot_plugins bp ON p.id = bp.plugin_id AND bp.is_active = 1
    WHERE p.is_active = 1
    GROUP BY p.id
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Представления созданы для удобного анализа в SQLiteStudio")

if __name__ == "__main__":
    init_database()
    create_views()
    print("\n🎮 Теперь вы можете открыть файл 'data/bot_constructor.db' в SQLiteStudio")
    print("📁 Полный путь: data/bot_constructor.db")