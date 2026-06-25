#!/bin/bash
# ─────────────────────────────────────────
# install.sh
# Instalacion de agro-bot
# ─────────────────────────────────────────

set -e

echo "=== Instalador agro-bot ==="
echo ""

# Dependencias base del sistema
echo "[1/3] Instalando dependencias del sistema..."
sudo apt update -q
sudo apt install -y git python3 python3-pip curl nano

# Dependencias Python
echo "[2/3] Instalando dependencias Python..."
pip3 install python-telegram-bot requests --break-system-packages

# Servicio systemd
echo "[3/3] Instalando servicio del sistema..."
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
echo "=== Configuracion pendiente ==="
echo "  cp src/config.py.ejemplo src/config.py"
echo "  nano src/config.py"
echo ""
echo "=== Servicio instalado pero NO activado ==="
echo "  Para activar manualmente:"
echo "  sudo systemctl enable agro-bot"
echo "  sudo systemctl start agro-bot"
echo ""
echo "  Para activar desde el panel: usar opcion [A] en el dashboard"
echo ""
echo "Listo!"
