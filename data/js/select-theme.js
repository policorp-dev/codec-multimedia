document.addEventListener('DOMContentLoaded', () => {
    const body = document.body;

    // Carregar o tema salvo no localStorage
    const darkMode = sessionStorage.getItem('dark-mode') === 'enabled';

    // Aplica a classe 'dark-mode' com base na preferência armazenada
    if (darkMode) {
        wrapper.classList.add('dark-mode');
    } else {
        wrapper.classList.remove('dark-mode');
    }

    // Alterna o tema e salva a preferência
    document.getElementById('theme-toggle').addEventListener('click', () => {
        wrapper.classList.toggle('dark-mode');
        sessionStorage.setItem('dark-mode', wrapper.classList.contains('dark-mode') ? 'enabled' : 'disabled');
    });
});

