from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO
import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

# Конфигурация Telegram бота для аутентификации
TELEGRAM_BOT_TOKEN = "8486531147:AAEGRILRHkTDMZ1oDIEX84SdP3Bq7GsK0VI"  # Замените на реальный токен

# Создаем папку для данных если нет
Path('data').mkdir(exist_ok=True)

# Создаем экземпляр Flask приложения
flask_app = Flask(__name__)
flask_app.secret_key = 'your-secret-key-here'
socketio = SocketIO(flask_app)

def get_db_connection():
    """Подключение к базе данных"""
    conn = sqlite3.connect('data/bot_constructor.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_user(telegram_id, username=None, first_name=None, last_name=None, photo_url=None):
    """Инициализация пользователя в базе данных"""
    conn = get_db_connection()
    try:
        conn.execute('''
        INSERT OR REPLACE INTO users (telegram_id, username, first_name, last_name, photo_url) 
        VALUES (?, ?, ?, ?, ?)
        ''', (telegram_id, username, first_name, last_name, photo_url))
        conn.commit()
        
        # Получаем ID пользователя
        user = conn.execute('SELECT id FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()
        return user['id'] if user else None
        
    except Exception as e:
        print(f"Ошибка инициализации пользователя: {e}")
        return None
    finally:
        conn.close()

@flask_app.route('/')
def index():
    # Если пользователь уже авторизован, перенаправляем на дашборд
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('index.html')

@flask_app.route('/telegram_login', methods=['POST'])
def telegram_login():
    """Обработка входа через Telegram Login Widget"""
    try:
        user_data = request.json
        print(f"Получены данные от Telegram: {user_data}")
        
        # Проверяем обязательные поля
        if not user_data or 'id' not in user_data:
            return jsonify({'success': False, 'error': 'Invalid user data'})
        
        telegram_id = user_data['id']
        username = user_data.get('username', '')
        first_name = user_data.get('first_name', '')
        last_name = user_data.get('last_name', '')
        photo_url = user_data.get('photo_url', '')
        
        # Инициализируем/обновляем пользователя в базе
        user_id = init_user(telegram_id, username, first_name, last_name, photo_url)
        
        if user_id:
            # Сохраняем в сессии
            session['user_id'] = telegram_id
            session['username'] = username
            session['first_name'] = first_name
            session['photo_url'] = photo_url
            session['is_telegram_login'] = True
            
            print(f"✅ Успешный вход через Telegram: {telegram_id} - {username}")
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Database error'})
            
    except Exception as e:
        print(f"❌ Ошибка входа через Telegram: {e}")
        return jsonify({'success': False, 'error': str(e)})

@flask_app.route('/webapp_login', methods=['POST'])
def webapp_login():
    """Обработка входа через Telegram WebApp"""
    try:
        data = request.json
        init_data = data.get('initData', '')
        
        if not init_data:
            return jsonify({'success': False, 'error': 'No init data'})
        
        # Для упрощения пока пропускаем проверку WebApp данных
        # В реальной реализации здесь должна быть проверка подписи
        
        # Создаем тестового пользователя
        telegram_id = 123456 + len(init_data)  # Простая генерация ID
        username = f"webapp_user_{telegram_id}"
        first_name = "WebApp"
        last_name = "User"
        
        # Инициализируем пользователя
        user_id = init_user(telegram_id, username, first_name, last_name)
        
        if user_id:
            session['user_id'] = telegram_id
            session['username'] = username
            session['first_name'] = first_name
            session['is_telegram_login'] = True
            session['is_webapp'] = True
            
            print(f"✅ Успешный вход через WebApp: {telegram_id} - {username}")
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Invalid Telegram data'})
        
    except Exception as e:
        print(f"❌ Ошибка входа через WebApp: {e}")
        return jsonify({'success': False, 'error': str(e)})

@flask_app.route('/logout')
def logout():
    """Выход из системы"""
    session.clear()
    return redirect('/')

@flask_app.route('/dashboard')
def show_dashboard():  # Переименовываем функцию чтобы избежать конфликта
    if 'user_id' not in session:
        return redirect('/')
    
    conn = get_db_connection()
    
    try:
        # Получаем пользователя
        user = conn.execute(
            'SELECT * FROM users WHERE telegram_id = ?', 
            (session['user_id'],)
        ).fetchone()
        
        if not user:
            return redirect('/logout')
        
        # Получаем ботов пользователя
        user_bots = conn.execute('''
            SELECT ub.*, 
                   COUNT(bs.id) as stats_count,
                   COALESCE(SUM(bs.messages_processed), 0) as total_messages
            FROM user_bots ub
            LEFT JOIN bot_stats bs ON ub.id = bs.bot_id
            WHERE ub.owner_id = ?
            GROUP BY ub.id
            ORDER BY ub.created_at DESC
        ''', (user['id'],)).fetchall()
        
        # Преобразуем команды из JSON для каждого бота
        bots_with_commands = []
        for bot in user_bots:
            bot_dict = dict(bot)
            try:
                bot_dict['commands'] = json.loads(bot_dict.get('commands', '[]'))
            except:
                bot_dict['commands'] = []
            bots_with_commands.append(bot_dict)
        
        return render_template('dashboard.html', 
                             user=dict(user),
                             bots=bots_with_commands,
                             is_telegram_login=session.get('is_telegram_login', False))
    
    except Exception as e:
        print(f"❌ Ошибка загрузки дашборда: {e}")
        return redirect('/')
    finally:
        conn.close()

@flask_app.route('/bot/<int:bot_id>')
def show_bot_editor(bot_id):  # Переименовываем функцию
    if 'user_id' not in session:
        return redirect('/')
    
    conn = get_db_connection()
    
    try:
        # Получаем пользователя по telegram_id
        user = conn.execute(
            'SELECT * FROM users WHERE telegram_id = ?', 
            (session['user_id'],)
        ).fetchone()
        
        if not user:
            print(f"❌ Пользователь с telegram_id {session['user_id']} не найден")
            return "User not found", 404
        
        print(f"✅ Найден пользователь: {user['id']} - {user['username']}")
        
        # Получаем бота с проверкой владельца (используем id пользователя из базы)
        bot = conn.execute('''
            SELECT ub.* 
            FROM user_bots ub
            WHERE ub.id = ? AND ub.owner_id = ?
        ''', (bot_id, user['id'])).fetchone()
        
        if not bot:
            print(f"❌ Бот {bot_id} не найден для пользователя {user['id']}")
            return "Bot not found", 404
        
        print(f"✅ Найден бот: {bot['bot_name']}")
        
        # Парсим JSON данные
        try:
            commands = json.loads(bot['commands'] or '[]')
        except:
            commands = []
        
        try:
            settings = json.loads(bot['settings'] or '{}')
        except:
            settings = {}
        
        bot_data = dict(bot)
        bot_data['commands'] = commands
        bot_data['settings'] = settings
        
        # Получаем доступные плагины
        plugins = conn.execute('''
            SELECT p.*, 
                   bp.is_active as bot_plugin_active,
                   bp.settings as bot_plugin_settings
            FROM plugins p
            LEFT JOIN bot_plugins bp ON p.id = bp.plugin_id AND bp.bot_id = ?
            WHERE p.is_active = 1
        ''', (bot_id,)).fetchall()
        
        plugins_data = [dict(plugin) for plugin in plugins]
        
        print(f"✅ Загружено {len(plugins_data)} плагинов")
        
        return render_template('bot_editor.html', 
                             bot=bot_data, 
                             plugins=plugins_data)
    
    except Exception as e:
        print(f"❌ Ошибка в функции bot_editor: {e}")
        return f"Internal Server Error: {e}", 500
    
    finally:
        conn.close()

@flask_app.route('/api/bot/<int:bot_id>', methods=['GET', 'PUT'])
def api_bot_handler(bot_id):  # Переименовываем функцию
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    
    try:
        # Получаем пользователя
        user = conn.execute(
            'SELECT * FROM users WHERE telegram_id = ?', 
            (session['user_id'],)
        ).fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if request.method == 'GET':
            bot = conn.execute(
                'SELECT * FROM user_bots WHERE id = ? AND owner_id = ?', 
                (bot_id, user['id'])
            ).fetchone()
            
            if bot:
                bot_data = dict(bot)
                try:
                    bot_data['commands'] = json.loads(bot_data['commands'] or '[]')
                except:
                    bot_data['commands'] = []
                try:
                    bot_data['settings'] = json.loads(bot_data['settings'] or '{}')
                except:
                    bot_data['settings'] = {}
                return jsonify(bot_data)
            return jsonify({'error': 'Bot not found'}), 404
        
        elif request.method == 'PUT':
            data = request.json
            commands_json = json.dumps(data.get('commands', []), ensure_ascii=False)
            settings_json = json.dumps(data.get('settings', {}), ensure_ascii=False)
            
            conn.execute('''
                UPDATE user_bots 
                SET commands = ?, welcome_message = ?, bot_name = ?, settings = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND owner_id = ?
            ''', (commands_json, data.get('welcome_message'), data.get('bot_name'), 
                  settings_json, bot_id, user['id']))
            conn.commit()
            
            return jsonify({'success': True})
    
    except Exception as e:
        print(f"❌ Ошибка API бота: {e}")
        return jsonify({'error': str(e)}), 500
    
    finally:
        conn.close()

@flask_app.route('/api/bot/<int:bot_id>/stats')
def api_bot_stats(bot_id):  # Переименовываем функцию
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    
    try:
        # Получаем пользователя
        user = conn.execute(
            'SELECT * FROM users WHERE telegram_id = ?', 
            (session['user_id'],)
        ).fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Статистика за последние 7 дней
        stats = conn.execute('''
            SELECT date, messages_processed, commands_executed, users_count
            FROM bot_stats 
            WHERE bot_id = ? AND date >= date('now', '-7 days')
            ORDER BY date DESC
        ''', (bot_id,)).fetchall()
        
        # Общая статистика
        total_stats = conn.execute('''
            SELECT 
                SUM(messages_processed) as total_messages,
                SUM(commands_executed) as total_commands,
                MAX(users_count) as max_users
            FROM bot_stats 
            WHERE bot_id = ?
        ''', (bot_id,)).fetchone()
        
        return jsonify({
            'recent_stats': [dict(row) for row in stats],
            'total_stats': dict(total_stats) if total_stats else {}
        })
    
    except Exception as e:
        print(f"❌ Ошибка статистики бота: {e}")
        return jsonify({'error': str(e)}), 500
    
    finally:
        conn.close()

@flask_app.route('/api/plugins', methods=['GET', 'POST'])
def api_plugins_handler():  # Переименовываем функцию
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    
    try:
        if request.method == 'GET':
            plugins = conn.execute('SELECT * FROM plugins WHERE is_active = 1').fetchall()
            return jsonify([dict(plugin) for plugin in plugins])
        
        elif request.method == 'POST':
            data = request.json
            plugin_id = data.get('plugin_id')
            bot_id = data.get('bot_id')
            action = data.get('action')  # 'activate' or 'deactivate'
            
            # Заглушка для реализации активации/деактивации плагинов
            return jsonify({'success': True, 'message': f'Plugin {action}d'})
    
    except Exception as e:
        print(f"❌ Ошибка API плагинов: {e}")
        return jsonify({'error': str(e)}), 500
    
    finally:
        conn.close()

# Экспортируем для использования в других модулях
app = flask_app

if __name__ == '__main__':
    # Проверяем инициализацию базы данных
    if not Path('data/bot_constructor.db').exists():
        print("⚠️ База данных не найдена. Запустите init_database.py сначала.")
    else:
        print("🚀 Запуск Flask приложения...")
        print("📧 Веб-интерфейс доступен по адресу: http://127.0.0.1:5000")
        socketio.run(flask_app, debug=True, host='0.0.0.0', port=5000)