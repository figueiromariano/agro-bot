#!/bin/bash
# ─────────────────────────────────────────
# install.sh
# Instalacion de dependencias para agro-bot
# ─────────────────────────────────────────

echo "Instalando dependencias de agro-bot..."

pip3 install python-telegram-bot requests --break-system-packages

echo ""
echo "Configuracion:"
echo "  cp src/config.py.ejemplo src/config.py"
echo "  nano src/config.py"
echo ""
echo "Uso:"
echo "  python3 src/bot.py"
echo ""
echo "Listo!"
