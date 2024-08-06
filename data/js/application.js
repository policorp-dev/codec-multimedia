const params = new URLSearchParams(window.location.search);
const appName = "Spotify"

setCursorBusy();
setTimeout(function () {
    cmd(`app-${appName}`);
}, 50);

document.getElementById('btn_install_app').addEventListener('click', function() {
    setCursorBusy();
    document.getElementById('btn_install_app').disabled = true;

    document.getElementById('pgr_install_app').innerHTML = '<img src="img/store/processing.gif" style="width:24px"/> Instalando. Aguarde...';
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

    document.getElementById('pgr_install_app').innerHTML = '<img src="img/store/processing.gif" style="width:24px"/> Removendo. Aguarde...';
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