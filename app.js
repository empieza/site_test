class App {
    constructor() {
        this.authService = new AuthService();
        this.dashboard = new Dashboard(this.authService);
        this.botEditor = new BotEditor();
        this.currentView = 'login';
        
        this.init();
    }

    async init() {
        // Проверяем авторизацию при загрузке
        const authData = await this.authService.checkAuth();
        
        if (authData) {
            this.showDashboard();
        } else {
            this.showLogin();
        }
    }

    // Показать логин
    showLogin() {
        document.getElementById('app').innerHTML = `
            <div class="login-page">
                <h1>Bot Constructor</h1>
                <div id="telegram-login"></div>
                <button onclick="app.demoLogin()">Демо вход</button>
            </div>
        `;
        
        // Инициализация Telegram Login Widget
        this.initTelegramWidget();
    }

    initTelegramWidget() {
        // Код для Telegram Login Widget
        const script = document.createElement('script');
        script.src = "https://telegram.org/js/telegram-widget.js?22";
        script.setAttribute('data-telegram-login', 'your_bot_username');
        script.setAttribute('data-size', 'large');
        script.setAttribute('data-onauth', 'app.onTelegramAuth(user)');
        script.setAttribute('data-request-access', 'write');
        document.getElementById('telegram-login').appendChild(script);
    }

    // Обработка авторизации Telegram
    async onTelegramAuth(user) {
        const result = await this.authService.telegramLogin(user);
        
        if (result.success) {
            this.showDashboard();
        } else {
            alert('Ошибка авторизации: ' + result.error);
        }
    }

    // Демо вход для тестирования
    async demoLogin() {
        const demoUser = {
            id: 123456789,
            first_name: 'Demo',
            username: 'demo_user'
        };
        
        await this.onTelegramAuth(demoUser);
    }

    // Показать дашборд
    async showDashboard() {
        try {
            const data = await this.dashboard.loadDashboard();
            document.getElementById('app').innerHTML = this.dashboard.renderDashboard(data);
        } catch (error) {
            this.showLogin();
        }
    }

    // Открыть редактор бота
    async openBotEditor(botId) {
        try {
            const botData = await this.botEditor.loadBot(botId);
            document.getElementById('app').innerHTML = this.botEditor.renderEditor(botData);
        } catch (error) {
            alert('Ошибка загрузки бота: ' + error.message);
        }
    }

    // Выход
    async logout() {
        await this.authService.logout();
        this.showLogin();
    }
}

// Инициализация приложения
const app = new App();