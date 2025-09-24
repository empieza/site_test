import time
import psutil
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass
from prometheus_client import Counter, Gauge, Histogram, start_http_server

@dataclass
class BotMetrics:
    messages_processed: int = 0
    commands_executed: int = 0
    errors_count: int = 0
    start_time: datetime = None
    last_activity: datetime = None

class PerformanceMonitor:
    def __init__(self):
        self.bots_metrics: Dict[int, BotMetrics] = {}
        self.system_metrics = {
            'cpu_usage': Gauge('bot_cpu_usage', 'CPU usage percentage'),
            'memory_usage': Gauge('bot_memory_usage', 'Memory usage in MB'),
            'active_bots': Gauge('active_bots_count', 'Number of active bots')
        }
        
        # Prometheus метрики
        self.messages_counter = Counter('messages_total', 'Total messages processed')
        self.response_time = Histogram('response_time_seconds', 'Response time histogram')
    
    def start_monitoring(self, port=8000):
        """Запуск метрик сервера"""
        start_http_server(port)
    
    def register_bot(self, bot_id: int):
        self.bots_metrics[bot_id] = BotMetrics(start_time=datetime.now())
    
    def record_message(self, bot_id: int):
        if bot_id in self.bots_metrics:
            self.bots_metrics[bot_id].messages_processed += 1
            self.bots_metrics[bot_id].last_activity = datetime.now()
        self.messages_counter.inc()
    
    def record_command(self, bot_id: int):
        if bot_id in self.bots_metrics:
            self.bots_metrics[bot_id].commands_executed += 1
    
    def record_error(self, bot_id: int):
        if bot_id in self.bots_metrics:
            self.bots_metrics[bot_id].errors_count += 1
    
    @response_time.time()
    def record_response_time(self, duration: float):
        pass
    
    async def collect_system_metrics(self):
        """Сбор системных метрик"""
        while True:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_metrics['cpu_usage'].set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_metrics['memory_usage'].set(memory.used / 1024 / 1024)
            
            # Active bots
            active_bots = len([b for b in self.bots_metrics.values() 
                             if b.last_activity and 
                             datetime.now() - b.last_activity < timedelta(minutes=5)])
            self.system_metrics['active_bots'].set(active_bots)
            
            await asyncio.sleep(10)
    
    def get_bot_stats(self, bot_id: int) -> Dict:
        if bot_id not in self.bots_metrics:
            return {}
        
        metrics = self.bots_metrics[bot_id]
        uptime = datetime.now() - metrics.start_time
        
        return {
            'messages_processed': metrics.messages_processed,
            'commands_executed': metrics.commands_executed,
            'errors_count': metrics.errors_count,
            'uptime': str(uptime).split('.')[0],
            'last_activity': metrics.last_activity.isoformat() if metrics.last_activity else None
        }