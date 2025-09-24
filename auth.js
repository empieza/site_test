const API_BASE_URL = 'https://empieza.github.io/site_test/'; // Замените на ваш URL

class AuthService {
    // Проверка авторизации
    async checkAuth() {
        try {
            const response = await fetch(`${API_BASE_URL}/dashboard`, {
                method: 'GET',
                credentials: 'include'
            });
            
            if (response.ok) {
                return await response.json();
            }
            return null;
        } catch (error) {
            console.error('Auth check failed:', error);
            return null;
        }
    }

    // Вход через Telegram
    async telegramLogin(userData) {
        try {
            const response = await fetch(`${API_BASE_URL}/telegram_login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData),
                credentials: 'include'
            });
            
            return await response.json();
        } catch (error) {
            console.error('Telegram login failed:', error);
            return { success: false, error: error.message };
        }
    }

    // Вход через WebApp
    async webappLogin(initData) {
        try {
            const response = await fetch(`${API_BASE_URL}/webapp_login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ initData }),
                credentials: 'include'
            });
            
            return await response.json();
        } catch (error) {
            console.error('WebApp login failed:', error);
            return { success: false, error: error.message };
        }
    }

    // Выход
    async logout() {
        try {
            await fetch(`${API_BASE_URL}/logout`, {
                method: 'POST',
                credentials: 'include'
            });
        } catch (error) {
            console.error('Logout failed:', error);
        }
    }
}