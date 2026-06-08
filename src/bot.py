#!/usr/bin/env python3
# ─────────────────────────────────────────
# bot.py
# Bot de Telegram para el proyecto Agro
# ─────────────────────────────────────────

import sys
import os
import logging
import socket
import time
import datetime
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import NetworkError, TimedOut
from httpx import ConnectError, ConnectTimeout, ReadTimeout

sys.path.insert(0, os.path.dirname(__file__))

from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, DISPOSITIVOS, FIREBASE_DATABASE_URL

import firebase_client as fb

logging.basicConfig(level=logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("telegram").setLevel(logging.CRITICAL)
logging.getLogger("telegram.ext.Application").setLevel(logging.CRITICAL)

# ─────────────────────────────────────────
def con_reintentos(func, *args, intentos=3, espera=5):
    for i in range(intentos):
        try:
            return func(*args)
        except Exception as e:
            if i < intentos - 1:
                time.sleep(espera)
            else:
                return None

# ─────────────────────────────────────────
def teclado_principal():
    return ReplyKeyboardMarkup([
        ["🌡 Ultima lectura", "📊 Historial"],
        ["📡 Estado del dispositivo", "🔧 Datos internos"],
        ["📈 Resumen del dia", "🤖 Estado del bot"],
        ["ℹ Ayuda"]
    ], resize_keyboard=True)

# ─────────────────────────────────────────
def publicar_estado_bot(corriendo):
    try:
        datos = {
            "corriendo": corriendo,
            "equipo": socket.gethostname(),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        for clave, valor in datos.items():
            url = f"{FIREBASE_DATABASE_URL}bots/agropanel_bot/{clave}.json"
            requests.put(url, json=valor)
    except:
        pass

# ─────────────────────────────────────────
async def cmd_estado_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = f"{FIREBASE_DATABASE_URL}bots/agropanel_bot.json"
        response = requests.get(url)
        datos = response.json()
        corriendo = datos.get("corriendo", False)
        equipo    = datos.get("equipo", "-")
        timestamp = datos.get("timestamp", "-")
        msg = (
            f"🤖 *Estado del bot*\n\n"
            f"Estado: *{'Corriendo' if corriendo else 'Detenido'}*\n"
            f"Equipo: `{equipo}`\n"
            f"Desde: {timestamp}"
        )
    except:
        msg = "No se pudo obtener el estado del bot."
    await update.message.reply_text(msg, parse_mode="Markdown")

# ─────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bienvenido al panel Agro 🌱\nEleji una opcion:",
        reply_markup=teclado_principal()
    )

# ─────────────────────────────────────────
async def ultima_lectura(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dispositivo = DISPOSITIVOS["dht11_esp32"]
    lectura = fb.obtener_ultima_lectura(dispositivo["ruta_sensores"])
    if not lectura:
        await update.message.reply_text("No se pudo obtener la lectura.")
        return
    msg = (
        f"🌡 *Sensor DHT11*\n\n"
        f"Temperatura: *{lectura.get('temperatura', '-')} °C*\n"
        f"Humedad: *{lectura.get('humedad', '-')} %*\n"
        f"Ultima lectura: {lectura.get('timestamp', '-')}"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# ─────────────────────────────────────────
async def historial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dispositivo = DISPOSITIVOS["dht11_esp32"]
    registros = fb.obtener_historial(dispositivo["ruta_sensores"], 10)
    if not registros:
        await update.message.reply_text("No hay historial disponible.")
        return
    msg = "📊 *Historial - ultimas 10 lecturas*\n\n"
    for clave, datos in registros:
        fecha, hora = clave.split("_")
        hora = hora.replace("-", ":")
        tmp = datos.get('temperatura', '-')
        hum = datos.get('humedad', '-')
        msg += f"`{fecha} {hora}` → {tmp}°C / {hum}%\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

# ─────────────────────────────────────────
async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    est = fb.obtener_estado_dispositivo("dht11_esp32")
    if not est:
        await update.message.reply_text("No se pudo obtener el estado.")
        return
    msg = (
        f"📡 *Estado del dispositivo*\n\n"
        f"Modo: *{est.get('modo', '-')}*\n"
        f"Red: {est.get('red', '-')}\n"
        f"IP: `{est.get('ip', '-')}`\n"
        f"Ultimo arranque: {est.get('ultimo_arranque', '-')}\n"
        f"Version: {est.get('version', '-')}"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# ─────────────────────────────────────────
async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "ℹ *Comandos disponibles*\n\n"
        "/start - Iniciar el bot\n"
        "🌡 Ultima lectura - Temperatura y humedad actual\n"
        "📊 Historial - Ultimas 10 lecturas\n"
        "📡 Estado del dispositivo - IP, red, modo\n"
        "🔧 Datos internos - RAM, señal WiFi, temp chip\n"
        "📈 Resumen del dia - Max, min, promedio\n"
        "🤖 Estado del bot - Equipo donde corre\n"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# ─────────────────────────────────────────
async def datos_internos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    datos = fb.leer("/dispositivos/dht11_esp32/sistema")
    if not datos:
        await update.message.reply_text("No se pudieron obtener los datos internos.")
        return

    ram_libre = datos.get("ram_libre", 0)
    ram_total = datos.get("ram_total", 0)
    ram_pct   = round((ram_libre / ram_total) * 100) if ram_total else 0

    rssi = datos.get("rssi", 0)
    if rssi >= -60:
        senal = "Excelente"
    elif rssi >= -70:
        senal = "Buena"
    elif rssi >= -80:
        senal = "Regular"
    else:
        senal = "Debil"

    uptime = datos.get("uptime", 0)
    horas  = uptime // 3600
    minutos = (uptime % 3600) // 60

    msg = (
        f"🔧 *Datos internos - esp32-galpon*\n\n"
        f"🌡 Temp chip: *{datos.get('temp_chip', '-')} °C*\n"
        f"💾 RAM libre: *{ram_libre} bytes ({ram_pct}%)*\n"
        f"📶 Señal WiFi: *{rssi} dBm ({senal})*\n"
        f"⏱ Uptime: *{horas}h {minutos}m*\n"
        f"🔄 Ultimo reset: {datos.get('causa_reset', '-')}\n"
        f"📟 MAC: `{datos.get('mac', '-')}`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# ─────────────────────────────────────────
async def resumen_dia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dispositivo = DISPOSITIVOS["dht11_esp32"]
    registros = fb.obtener_historial(dispositivo["ruta_sensores"], 50)
    if not registros:
        await update.message.reply_text("No hay datos suficientes para el resumen.")
        return

    temps = [d.get("temperatura") for _, d in registros if d.get("temperatura")]
    hums  = [d.get("humedad") for _, d in registros if d.get("humedad")]

    if not temps:
        await update.message.reply_text("No hay datos de temperatura disponibles.")
        return

    temp_max  = max(temps)
    temp_min  = min(temps)
    temp_prom = round(sum(temps) / len(temps), 1)
    hum_prom  = round(sum(hums) / len(hums)) if hums else "-"

    ultima = registros[0]
    temp_actual = ultima[1].get("temperatura", "-")
    temp_ant    = registros[1][1].get("temperatura", 0) if len(registros) > 1 else temp_actual
    tendencia = "↑ Subiendo" if temp_actual > temp_ant else "↓ Bajando" if temp_actual < temp_ant else "→ Estable"

    msg = (
        f"📈 *Resumen del dia*\n\n"
        f"🌡 Temperatura\n"
        f"  Max: *{temp_max} °C*\n"
        f"  Min: *{temp_min} °C*\n"
        f"  Promedio: *{temp_prom} °C*\n"
        f"  Tendencia: {tendencia}\n\n"
        f"💧 Humedad promedio: *{hum_prom} %*\n"
        f"📊 Basado en {len(temps)} lecturas"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# ─────────────────────────────────────────
async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    if "Ultima lectura" in texto:
        await ultima_lectura(update, context)
    elif "Historial" in texto:
        await historial(update, context)
    elif "Datos internos" in texto:
        await datos_internos(update, context)
    elif "Resumen del dia" in texto:
        await resumen_dia(update, context)
    elif "Estado del bot" in texto:
        await cmd_estado_bot(update, context)
    elif "Estado" in texto:
        await estado(update, context)
    elif "Ayuda" in texto:
        await ayuda(update, context)
    else:
        await update.message.reply_text(
            "No entendi. Usa los botones del menu.",
            reply_markup=teclado_principal()
        )

# ─────────────────────────────────────────
def main():
    publicar_estado_bot(True)
    print("Bot iniciado. Ctrl+C para detener.")

    while True:
        try:
            app = Application.builder().token(TELEGRAM_TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("estado", cmd_estado_bot))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))
            app.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
        except KeyboardInterrupt:
            print("Bot detenido manualmente.")
            publicar_estado_bot(False)
            break
        except (NetworkError, TimedOut, ConnectError, ConnectTimeout, ReadTimeout) as e:
            print(f"Error de conexion: {e}")
            print("Reintentando en 30 segundos...")
            time.sleep(30)
            print("Reconectando...")
        except Exception as e:
            print(f"Error inesperado: {e}")
            print("Reintentando en 60 segundos...")
            time.sleep(60)
            print("Reconectando...")

if __name__ == "__main__":
    main()
