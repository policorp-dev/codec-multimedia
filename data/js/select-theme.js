function detectTheme() {
    const darkThemeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    if (darkThemeMediaQuery.matches) {
        console.log('Tema atual: Escuro');
        // Adicione sua lógica para o tema escuro aqui
    } else {
        console.log('Tema atual: Claro');
        // Adicione sua lógica para o tema claro aqui
    }

// Adicionar listener para alterações de tema
    darkThemeMediaQuery.addEventListener('change', (event) => {
        if (event.matches) {
                console.log('Mudou para tema escuro');
            const body = document.body;
            const darkMode = localStorage.getItem('dark-mode') === 'enabled';
        wrapper.classList.toggle('dark-mode');
        // Atualize a lógica para o tema escuro aqui
        } else {
            console.log('Mudou para tema claro');
            const body = document.body;
            const darkMode = localStorage.getItem('dark-mode') === 'disabled';
        wrapper.classList.toggle('dark-mode');
        // Atualize a lógica para o tema claro aqui
        }
    });
}

// Chame a função ao carregar a aplicação
detectTheme();
