class Dashboard {
    constructor(authService) {
        this.authService = authService;
    }

    // Загрузка данных дашборда
    async loadDashboard() {
        try {
            const response = await fetch(`${API_BASE_URL}/dashboard`, {
                method: 'GET',
                credentials: 'include'
            });
            
            if (response.ok) {
                return await response.json();
            }
            throw new Error('Failed to load dashboard');
        } catch (error) {
            console.error('Dashboard load failed:', error);
            throw error;
        }
    }

    // Создание интерфейса дашборда
    renderDashboard(data) {
        return `
            <div class="dashboard">
                <header>
                    <h1>Добро пожаловать, ${data.user.first_name}!</h1>
                    <button onclick="app.logout()">Выйти</button>
                </header>
                
                <div class="bots-list">
                    ${data.bots.map(bot => this.renderBotCard(bot)).join('')}
                </div>
            </div>
        `;
    }

    renderBotCard(bot) {
        return `
            <div class="bot-card" onclick="app.openBotEditor(${bot.id})">
                <h3>${bot.bot_name}</h3>
                <p>Токен: ${bot.bot_token ? '***' + bot.bot_token.slice(-4) : 'Не установлен'}</p>
                <p>Сообщений: ${bot.total_messages || 0}</p>
            </div>
        `;
    }
}