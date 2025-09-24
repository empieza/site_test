import importlib
import inspect
from typing import Dict, List, Any
from abc import ABC, abstractmethod

class Plugin(ABC):
    """Базовый класс для плагинов"""
    
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def get_commands(self) -> List[Dict]:
        pass
    
    @abstractmethod
    def setup(self, bot_instance: Any):
        pass

class WeatherPlugin(Plugin):
    def get_name(self):
        return "Weather Plugin"
    
    def get_commands(self):
        return [
            {
                'name': 'weather',
                'description': 'Получить погоду',
                'response': 'Введите город для получения погоды'
            }
        ]
    
    def setup(self, bot_instance):
        @bot_instance.dp.message(Command("weather"))
        async def weather_command(message: types.Message):
            # Здесь можно интегрировать с API погоды
            await message.answer("Функция погоды в разработке")

class PaymentPlugin(Plugin):
    def get_name(self):
        return "Payment Plugin"
    
    def get_commands(self):
        return [
            {
                'name': 'pay',
                'description': 'Оплатить услугу',
                'response': 'Выберите способ оплаты'
            }
        ]
    
    def setup(self, bot_instance):
        @bot_instance.dp.message(Command("pay"))
        async def pay_command(message: types.Message):
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💳 Карта", callback_data="pay_card")],
                [InlineKeyboardButton(text="👛 Crypto", callback_data="pay_crypto")]
            ])
            await message.answer("Выберите способ оплаты:", reply_markup=keyboard)

class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.available_plugins = {
            'weather': WeatherPlugin,
            'payment': PaymentPlugin
        }
    
    def load_plugin(self, plugin_name: str) -> bool:
        if plugin_name in self.available_plugins:
            plugin_class = self.available_plugins[plugin_name]
            self.plugins[plugin_name] = plugin_class()
            return True
        return False
    
    def get_plugin_commands(self) -> List[Dict]:
        commands = []
        for plugin in self.plugins.values():
            commands.extend(plugin.get_commands())
        return commands
    
    def setup_plugins(self, bot_instance):
        for plugin in self.plugins.values():
            plugin.setup(bot_instance)