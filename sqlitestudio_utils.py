import sqlite3
import json
from datetime import datetime, timedelta

def generate_sample_data():
    """Генерация демонстрационных данных для SQLiteStudio"""
    
    conn = sqlite3.connect('data/bot_constructor.db')
    cursor = conn.cursor()
    
    try:
        # Генерируем статистику за последние 30 дней для тестового бота
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(30):
            date = base_date + timedelta(days=i)
            messages = max(10, 50 + i * 3 - (i % 7) * 20)  # Имитация недельной цикличности
            commands = messages // 3
            users = max(5, 10 + i - (i % 14) * 5)  # Рост пользователей
            
            cursor.execute('''
            INSERT OR REPLACE INTO bot_stats 
            (bot_id, date, messages_processed, commands_executed, users_count) 
            VALUES (?, ?, ?, ?, ?)
            ''', (1, date.strftime('%Y-%m-%d'), messages, commands, users))
        
        # Генерируем логи
        log_messages = [
            ("INFO", "Бот запущен успешно"),
            ("INFO", "Обработано 10 сообщений"),
            ("WARNING", "Высокая нагрузка на сервер"),
            ("ERROR", "Ошибка подключения к API"),
            ("INFO", "Новый пользователь присоединился"),
        ]
        
        for level, message in log_messages:
            cursor.execute('''
            INSERT INTO bot_logs (bot_id, level, message) 
            VALUES (?, ?, ?)
            ''', (1, level, message))
        
        conn.commit()
        print("✅ Демонстрационные данные сгенерированы для SQLiteStudio")
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка генерации данных: {e}")
    
    finally:
        conn.close()

def export_database_schema():
    """Экспорт схемы базы данных для документации"""
    
    conn = sqlite3.connect('data/bot_constructor.db')
    cursor = conn.cursor()
    
    # Получаем список таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    schema = {
        'database': 'bot_constructor',
        'tables': {}
    }
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        schema['tables'][table_name] = {
            'columns': [
                {
                    'name': col[1],
                    'type': col[2],
                    'nullable': not col[3],
                    'primary_key': col[5] == 1
                }
                for col in columns
            ]
        }
    
    conn.close()
    
    # Сохраняем схему в файл
    with open('database_schema.json', 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    
    print("✅ Схема базы данных экспортирована в database_schema.json")

if __name__ == "__main__":
    generate_sample_data()
    export_database_schema()