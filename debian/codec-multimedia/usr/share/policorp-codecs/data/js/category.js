// Obter o parâmetro 'category' da URL
const params = new URLSearchParams(window.location.search);
const category = params.get('category');

setCursorBusy();
setTimeout(function () {
    cmd(`category-${category}`);
}, 50);

function openApp(application) {
    smoothPageFade("application.html", { application: application });
}
