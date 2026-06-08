# Agro Bot

Bot de Telegram para el proyecto Agro de monitoreo agricola-ganadero.

## Descripcion

Bot que permite consultar el estado de los sensores del proyecto Agro
directamente desde Telegram, en cualquier momento y desde cualquier
dispositivo. Lee los datos de Firebase Realtime Database.

## Funciones

- Ver ultima lectura del sensor (temperatura y humedad)
- Ver historial de las ultimas 10 lecturas
- Ver resumen del dia (max, min, promedio, tendencia)
- Ver estado del dispositivo (modo, red WiFi, IP, ultimo arranque)
- Ver datos internos del ESP32 (RAM, señal WiFi, temperatura del chip)
- Ver estado del bot (equipo donde esta corriendo)
- Reconexion automatica ante cortes de internet

## Tecnologias

- Python 3
- python-telegram-bot
- Firebase Realtime Database

## Dispositivos soportados

| Dispositivo | Firebase path |
|-------------|--------------|
| esp32-galpon | /dispositivos/dht11_esp32 |

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

O usar el instalador:

    bash install.sh

Copiar y completar la configuracion:

    cp src/config.py.ejemplo src/config.py
    nano src/config.py

## Uso

Correr directamente:

    python3 src/bot.py

Como servicio del sistema:

    sudo systemctl start agro-bot
    sudo systemctl enable agro-bot  # inicio automatico

## Estado

En desarrollo
