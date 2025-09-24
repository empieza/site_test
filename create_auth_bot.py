import os
from telegram import Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters

class AuthBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        # Команда /start
        self.application.add_handler(CommandHandler("start", self.start_command))
        
        # Обработка текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo_message))
    
    async def start_command(self, update, context):
        """Обработка команды /start"""
        user = update.effective_user
        welcome_text = f"""
🤖 Добро пожаловать в Bot Constructor!

С помощью этого бота вы можете:
• Создавать своих Telegram ботов
• Управлять ботами через веб-интерфейс
• Настраивать команды и плагины

📱 Для начала работы откройте веб-интерфейс:
http://your-server.com

Или используйте кнопку меню ниже.
        """
        
        # Отправляем сообщение с кнопкой
        keyboard = [
            [{"text": "🌐 Открыть веб-интерфейс", "url": "http://your-server.com"}],
            [{"text": "📊 Мои боты", "web_app": {"url": "http://your-server.com"}}]
        ]
        
        reply_markup = {"inline_keyboard": keyboard}
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup
        )
    
    async def echo_message(self, update, context):
        """Обработка обычных сообщений"""
        await update.message.reply_text(
            "Откройте веб-интерфейс для управления ботами: http://your-server.com"
        )
    
    def run(self):
        """Запуск бота"""
        print("🤖 Бот аутентификации запущен...")
        self.application.run_polling()

if __name__ == "__main__":
    # Токен вашего бота для аутентификации
    BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
    
    if BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("❌ Замените BOT_TOKEN на реальный токен от @BotFather")
    else:
        bot = AuthBot(BOT_TOKEN)
        bot.run()