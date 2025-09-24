import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class BotMigration:
    def __init__(self):
        self.migrations_dir = Path("migrations")
        self.migrations_dir.mkdir(exist_ok=True)
    
    def export_bot(self, bot_id: int, bot_data: Dict) -> str:
        """Экспорт бота в файл"""
        export_data = {
            'version': '1.0',
            'export_date': datetime.now().isoformat(),
            'bot_data': bot_data,
            'files': self._collect_bot_files(bot_id)
        }
        
        filename = f"bot_{bot_id}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        export_path = self.migrations_dir / filename
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return str(export_path)
    
    def import_bot(self, import_file: str, new_owner_id: int) -> Dict:
        """Импорт бота из файла"""
        with open(import_file, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        bot_data = import_data['bot_data']
        bot_data['owner_id'] = new_owner_id
        bot_data['bot_token'] = ''  # Токен нужно будет установить заново
        
        return bot_data
    
    def _collect_bot_files(self, bot_id: int) -> Dict:
        """Сбор файлов бота"""
        bot_dir = Path(f"user_bots/bot_{bot_id}")
        files = {}
        
        if bot_dir.exists():
            for file_path in bot_dir.glob('*'):
                if file_path.is_file():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        files[file_path.name] = f.read()
        
        return files
    
    def migrate_bot_version(self, bot_id: int, from_version: str, to_version: str):
        """Миграция бота между версиями"""
        migration_scripts = {
            '1.0->1.1': self._migrate_1_0_to_1_1,
            '1.1->1.2': self._migrate_1_1_to_1_2
        }
        
        migration_key = f"{from_version}->{to_version}"
        if migration_key in migration_scripts:
            migration_scripts[migration_key](bot_id)
    
    def _migrate_1_0_to_1_1(self, bot_id: int):
        """Миграция с версии 1.0 на 1.1"""
        # Добавление новых полей и преобразование данных
        pass
    
    def _migrate_1_1_to_1_2(self, bot_id: int):
        """Миграция с версии 1.1 на 1.2"""
        # Обновление структуры команд
        pass

class BackupManager:
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self):
        """Создание резервной копии всей системы"""
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.backup_dir / backup_name
        
        # Копируем базу данных
        shutil.copy2('bot_constructor.db', backup_path / 'database.db')
        
        # Копируем пользовательских ботов
        if Path('user_bots').exists():
            shutil.copytree('user_bots', backup_path / 'user_bots')
        
        # Создаем файл метаданных
        metadata = {
            'backup_date': datetime.now().isoformat(),
            'version': '1.0',
            'file_count': len(list(backup_path.rglob('*')))
        }
        
        with open(backup_path / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return backup_path