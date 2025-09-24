import hashlib
import hmac
import json
import urllib.parse
from typing import Optional, Dict

class TelegramAuth:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
    
    def verify_telegram_webapp(self, init_data: str) -> bool:
        """Упрощенная проверка WebApp данных (для демонстрации)"""
        # В реальном приложении здесь должна быть полная проверка подписи
        # Для демонстрации возвращаем True
        return True
    
    def get_user_data(self, init_data: str) -> Optional[Dict]:
        """Извлекаем данные пользователя из initData"""
        try:
            pairs = init_data.split('&')
            user_data_str = None
            
            for pair in pairs:
                if pair.startswith('user='):
                    user_data_str = urllib.parse.unquote(pair[5:])  # Убираем 'user='
                    break
            
            if user_data_str:
                return json.loads(user_data_str)
            return None
            
        except Exception as e:
            print(f"Ошибка извлечения данных пользователя: {e}")
            return None

# Глобальный экземпляр для аутентификации
telegram_auth = None

def init_telegram_auth(bot_token: str):
    """Инициализация системы аутентификации"""
    global telegram_auth
    telegram_auth = TelegramAuth(bot_token)
    return telegram_auth