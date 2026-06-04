#!/bin/bash
# ─────────────────────────────────────────
# install.sh
# Instalacion de agro-bot
# ─────────────────────────────────────────

echo "Instalando dependencias de agro-bot..."
pip3 install python-telegram-bot requests --break-system-packages

echo "Instalando servicio del sistema..."
cat > /tmp/agro-bot.service << 'SERVICE'
[Unit]
Description=Agro Bot - Bot de Telegram para el proyecto Agro
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=INSTALL_DIR
ExecStart=/usr/bin/python3 INSTALL_DIR/src/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

sed -i "s|INSTALL_DIR|$(pwd)|g" /tmp/agro-bot.service
sudo mv /tmp/agro-bot.service /etc/systemd/system/agro-bot.service
sudo systemctl daemon-reload

echo ""
echo "Servicio instalado pero NO activado."
echo "Para activarlo usar el panel o manualmente:"
echo "  sudo systemctl enable agro-bot"
echo "  sudo systemctl start agro-bot"
echo ""
echo "Configuracion:"
echo "  cp src/config.py.ejemplo src/config.py"
echo "  nano src/config.py"
echo ""
echo "Uso directo:"
echo "  python3 src/bot.py"
echo ""
echo "Listo!"
