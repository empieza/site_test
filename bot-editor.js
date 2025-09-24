class BotEditor {
    // Загрузка данных бота
    async loadBot(botId) {
        try {
            const response = await fetch(`${API_BASE_URL}/bot/${botId}`, {
                method: 'GET',
                credentials: 'include'
            });
            
            if (response.ok) {
                return await response.json();
            }
            throw new Error('Failed to load bot data');
        } catch (error) {
            console.error('Bot load failed:', error);
            throw error;
        }
    }

    // Сохранение бота
    async saveBot(botId, data) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/bot/${botId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
                credentials: 'include'
            });
            
            return await response.json();
        } catch (error) {
            console.error('Bot save failed:', error);
            return { success: false, error: error.message };
        }
    }

    // Рендер редактора
    renderEditor(botData) {
        return `
            <div class="bot-editor">
                <header>
                    <button onclick="app.showDashboard()">← Назад</button>
                    <h2>Редактор: ${botData.bot.bot_name}</h2>
                </header>
                
                <div class="editor-content">
                    <div class="commands-section">
                        <h3>Команды</h3>
                        ${this.renderCommands(botData.bot.commands)}
                    </div>
                    
                    <div class="plugins-section">
                        <h3>Плагины</h3>
                        ${this.renderPlugins(botData.plugins)}
                    </div>
                </div>
            </div>
        `;
    }

    renderCommands(commands) {
        // Логика рендера команд
        return commands.map(cmd => `
            <div class="command-item">
                <input type="text" value="${cmd.command}" placeholder="/command">
                <input type="text" value="${cmd.description}" placeholder="Описание">
                <textarea>${cmd.response}</textarea>
            </div>
        `).join('');
    }

    renderPlugins(plugins) {
        return plugins.map(plugin => `
            <div class="plugin-item">
                <h4>${plugin.name}</h4>
                <p>${plugin.description}</p>
                <button onclick="app.togglePlugin(${plugin.id}, ${plugin.bot_plugin_active})">
                    ${plugin.bot_plugin_active ? 'Выключить' : 'Включить'}
                </button>
            </div>
        `).join('');
    }
}