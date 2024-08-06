## Policorp-store

A aplicação é uma interface gráfica que permite aos usuários explorar, instalar e gerenciar uma variedade de aplicativos utilizando o Flatpak. Proporcionando uma maneira conveniente e eficiente de descobrir e usar software no ecossistema Linux, fornecendo uma experiência similar à de lojas de aplicativos em outras plataformas.

### Como listar aplicativos a loja

no arquivo localizado em `src/metadata.json` é possível listar os aplicativos que desejar disponiveis na loja do flathub: https://flathub.org/ 

Para exemplo será listado a aplicação Google Chrome(https://flathub.org/apps/com.google.Chrome)
Como é possível ver pelo URL o identificador é dado como **"com.google.Chrome"**. Com esta informação podemos continuar a listagem, o arquivo metadata.json possui a seguinte estrutura:
```json
{
    "name": "nome-do-app",
    "exec": "id-do-app",
    "icon": "/usr/share/policorp-store/resources/icone-png",
    "repo": "flatpak",
    "category": "categoria",
    "description": "descricao do app"
}
```
o arquivo modificado tera a seguinte estrutura:
```json
{
"name": "Google Chrome",
"exec": "com.google.Chrome",
"icon": "/usr/share/policorp-store/resources/chrome.png",
"repo": "flatpak",
"category": "Internet" ,
"description": "O Chrome é um navegador da web desenvolvido pela Google. Ele é conhecido por sua velocidade, desempenho e recursos avançados. O Chrome oferece uma experiência de navegação rápida e suave, permitindo que os usuários acessem sites, executem aplicativos da web e realizem pesquisas na internet de forma eficiente. Além disso, o Chrome possui recursos de segurança robustos, como navegação segura e proteção contra phishing, o que ajuda a manter os usuários protegidos durante a navegação online. O Chrome também oferece suporte a extensões, permitindo que os usuários personalizem e aprimorem sua experiência de navegação de acordo com suas necessidades e preferências."
}
```
após isto, basta abrir o aplicativo e a aplicação sera listada

### Categorias definidas

Dentro do arquivo src/metadata.json, é possível localizar o vetor "categories", onde é possível adicionar, remover as categorias desejadas. **É importante deixar a categoria "Mais aplicativos" por ultimo**.



