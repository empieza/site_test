#!/usr/bin/env python3
"""
Advanced Bot Constructor - Запуск системы
"""

import os
import sys
from pathlib import Path

# Добавляем текущую директорию в путь Python
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def check_environment():
    """Проверка окружения и зависимостей"""
    print("🔍 Проверка окружения...")
    
    # Проверяем наличие необходимых файлов
    required_files = ['web_app.py', 'advanced_main.py', 'templates/index.html']
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Отсутствует файл: {file}")
            return False
    
    # Проверяем наличие папки templates
    if not Path('templates').exists():
        print("❌ Отсутствует папка templates")
        return False
    
    print("✅ Окружение проверено успешно")
    return True

def install_dependencies():
    """Установка зависимостей"""
    print("📦 Проверка зависимостей...")
    
    try:
        import flask
        import sqlite3
        import jinja2
        import prometheus_client
        print("✅ Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствуют зависимости: {e}")
        print("Установите зависимости: pip install -r requirements_advanced.txt")
        return False

def main():
    """Основная функция запуска"""
    print("🚀 Advanced Bot Constructor")
    print("=" * 40)
    
    # Проверяем окружение
    if not check_environment():
        sys.exit(1)
    
    # Проверяем зависимости
    if not install_dependencies():
        sys.exit(1)
    
    # Запускаем основное приложение
    try:
        from advanced_main import main as app_main
        import asyncio
        asyncio.run(app_main())
    except KeyboardInterrupt:
        print("\n⏹️ Приложение остановлено")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()