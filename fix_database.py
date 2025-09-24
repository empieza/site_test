import sqlite3
import json

def fix_database_relationships():
    """Исправляем связи между пользователями и ботами"""
    
    conn = sqlite3.connect('data/bot_constructor.db')
    cursor = conn.cursor()
    
    try:
        print("🔍 Проверка базы данных...")
        
        # Проверяем существующих пользователей
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        print(f"📊 Найдено пользователей: {len(users)}")
        
        for user in users:
            print(f"👤 Пользователь: ID={user[0]}, Telegram ID={user[1]}, Username={user[2]}")
        
        # Проверяем существующих ботов
        cursor.execute("SELECT * FROM user_bots")
        bots = cursor.fetchall()
        print(f"🤖 Найдено ботов: {len(bots)}")
        
        for bot in bots:
            print(f"🤖 Бот: ID={bot[0]}, Owner ID={bot[1]}, Name={bot[3]}")
            
            # Проверяем, существует ли владелец
            cursor.execute("SELECT id FROM users WHERE id = ?", (bot[1],))
            owner_exists = cursor.fetchone()
            
            if not owner_exists:
                print(f"❌ У бота {bot[0]} не найден владелец с ID {bot[1]}")
                
                # Назначаем первого пользователя как владельца
                if users:
                    new_owner_id = users[0][0]
                    cursor.execute("UPDATE user_bots SET owner_id = ? WHERE id = ?", 
                                 (new_owner_id, bot[0]))
                    print(f"✅ Назначен новый владелец: {new_owner_id}")
        
        conn.commit()
        print("✅ Проверка и исправление завершены!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    finally:
        conn.close()

def create_test_user_and_bot():
    """Создаем тестового пользователя и бота для демонстрации"""
    
    conn = sqlite3.connect('data/bot_constructor.db')
    cursor = conn.cursor()
    
    try:
        # Создаем тестового пользователя
        cursor.execute('''
        INSERT OR IGNORE INTO users (telegram_id, username, first_name, last_name) 
        VALUES (?, ?, ?, ?)
        ''', (123456, 'test_user', 'Тест', 'Пользователь'))
        
        # Получаем ID созданного пользователя
        cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (123456,))
        user_id = cursor.fetchone()[0]
        print(f"✅ Создан пользователь с ID: {user_id}")
        
        # Создаем тестового бота
        test_commands = json.dumps([
            {'name': 'start', 'response': 'Добро пожаловать в тестового бота!'},
            {'name': 'help', 'response': 'Это помощь по тестовому боту'},
            {'name': 'info', 'response': 'Информация о тестовом боте'}
        ], ensure_ascii=False)
        
        cursor.execute('''
        INSERT OR REPLACE INTO user_bots 
        (owner_id, bot_token, bot_username, bot_name, commands, welcome_message, is_active) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, '123456789:TESTBOTtoken123456789', 'test_bot', 
              'Тестовый бот', test_commands, 'Привет! Я тестовый бот.', 1))
        
        conn.commit()
        print("✅ Тестовый бот создан успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка создания тестовых данных: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🛠️ Исправление базы данных...")
    fix_database_relationships()
    create_test_user_and_bot()
    print("\n🎯 Теперь откройте http://127.0.0.1:5000 и войдите с тестовыми данными:")
    print("   User ID: 123456")
    print("   Username: test_user")