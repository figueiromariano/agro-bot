#!/bin/bash
# ─────────────────────────────────────────
# uninstall.sh
# Desinstalacion de agro-bot
# ─────────────────────────────────────────

echo "=== Desinstalador agro-bot ==="
echo ""

# Detener y deshabilitar servicio
echo "[1/3] Deteniendo servicio..."
sudo systemctl stop agro-bot 2>/dev/null || true
sudo systemctl disable agro-bot 2>/dev/null || true

# Eliminar servicio
echo "[2/3] Eliminando servicio del sistema..."
sudo rm -f /etc/systemd/system/agro-bot.service
sudo systemctl daemon-reload

# Desinstalar dependencias Python
echo "[3/3] Desinstalando dependencias Python..."
pip3 uninstall -y python-telegram-bot requests 2>/dev/null || true

echo ""
echo "agro-bot desinstalado."
echo "Los archivos del repositorio NO fueron eliminados."
echo "Para eliminar completamente: rm -rf $(pwd)"
echo ""
echo "Listo!"
