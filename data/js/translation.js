function applyLanguage(language) {
	document.querySelectorAll('[data-lang-en], [data-lang-pt]').forEach(el => {
		const text = el.getAttribute(`data-lang-${language}`);
                if (text) {
                    el.tagName === "TITLE" ? (document.title = text) : (el.textContent = text);
                }
            });
}

        // Detect browser language or use default
const userLang = navigator.language.startsWith('pt') ? 'pt' : 'en';
applyLanguage(userLang);
