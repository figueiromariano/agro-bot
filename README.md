# Agro Bot

Bot de Telegram para el proyecto Agro de monitoreo agricola-ganadero.

## Descripcion

Bot que permite consultar el estado de los sensores del proyecto Agro
directamente desde Telegram, en cualquier momento y desde cualquier dispositivo.

## Funciones

- Ver ultima lectura del sensor (temperatura y humedad)
- Ver historial de las ultimas 10 lecturas
- Ver estado del dispositivo (modo, red WiFi, IP, ultimo arranque)

## Tecnologias

- Python 3
- python-telegram-bot
- Firebase Realtime Database

## Repositorios relacionados

- [campo-sensores](https://github.com/figueiromariano/campo-sensores)
- [agro-panel](https://github.com/figueiromariano/agro-panel)
- [agente-campo](https://github.com/figueiromariano/agente-campo)

## Instalacion

Clonar el repositorio:

    git clone https://github.com/figueiromariano/agro-bot.git
    cd agro-bot

Instalar dependencias:

    pip3 install python-telegram-bot requests --break-system-packages

Copiar y completar la configuracion:

    cp src/config.py.ejemplo src/config.py

Editar src/config.py con tus credenciales.

## Uso

    python3 src/bot.py

## Estado

En desarrollo
