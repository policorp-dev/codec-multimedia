const params = new URLSearchParams(window.location.search);
const appName = "codecs"

setCursorBusy();
setTimeout(function () {
    cmd(`app-${appName}`);
}, 50);

function updateProcessText(action) {
    const lang = navigator.language || navigator.userLanguage;

    // Define os textos para português e inglês
    const messages = {
        'pt-BR': {
            install: 'Instalando. Aguarde...',
            remove: 'Removendo. Aguarde...'
        },
        'en': {
            install: 'Installing. Please wait...',
            remove: 'Removing. Please wait...'
        }
    };

    // Define o texto com base no idioma e na ação (install/remove)
    const processText = messages[lang] && messages[lang][action] || messages['en'][action];  // Se o idioma não for encontrado, usa o inglês

    // Atualiza o texto da barra de progresso
    document.getElementById('pgr_install_app').innerHTML = `<img src="img/store/processing.gif" style="width:24px"/> ${processText}`;
}

document.getElementById('btn_install_app').addEventListener('click', function() {
    setCursorBusy();
    document.getElementById('btn_install_app').disabled = true;

   // document.getElementById('pgr_install_app').innerHTML = '<img src="img/store/processing.gif" style="width:24px"/> Instalando. Aguarde...';
    updateProcessText('install');
    document.getElementById('pgr_install_app').classList.remove('d-none');
    document.getElementById('pgr_install_app').classList.add('d-block');

    document.getElementById('section_log').classList.remove('d-none');
    document.getElementById('section_log').classList.add('d-block');

    setTimeout(function () {
        cmd(`flatpak-install`);
    }, 500);
});

document.getElementById('btn_remove_app').addEventListener('click', function() {
    setCursorBusy();
    document.getElementById('btn_open_app').disabled = true;
    document.getElementById('btn_remove_app').disabled = true;

    updateProcessText('remove');
    //document.getElementById('pgr_install_app').innerHTML = '<img src="img/store/processing.gif" style="width:24px"/> Removendo. Aguarde...';
    document.getElementById('pgr_install_app').classList.remove('d-none');
    document.getElementById('pgr_install_app').classList.add('d-block');

    document.getElementById('section_log').classList.remove('d-none');
    document.getElementById('section_log').classList.add('d-block');

    setTimeout(function () {
        cmd(`flatpak-remove`);
    }, 500);
});

document.getElementById('btn_open_app').addEventListener('click', function() {
    setCursorBusy();
    document.getElementById('btn_open_app').disabled = true;
    document.getElementById('btn_remove_app').disabled = true;

    setTimeout(function () {
        cmd(`flatpak-open`);
    }, 100);
});
