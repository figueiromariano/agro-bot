#!/usr/bin/env python3
# ─────────────────────────────────────────
# bot.py
# Bot de Telegram para el proyecto Agro
# ─────────────────────────────────────────

import sys
import os
import logging
import socket
import datetime
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

sys.path.insert(0, os.path.dirname(__file__))

from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, DISPOSITIVOS, FIREBASE_DATABASE_URL

import firebase_client as fb

logging.basicConfig(level=logging.WARNING)

# ─────────────────────────────────────────
def teclado_principal():
    return ReplyKeyboardMarkup([
        ["🌡 Ultima lectura", "📊 Historial"],
        ["📡 Estado del dispositivo", "🤖 Estado del bot"],
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
        "🌡 Ultima lectura - Ver temperatura y humedad\n"
        "📊 Historial - Ver ultimas 10 lecturas\n"
        "📡 Estado - Ver estado del dispositivo\n"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# ─────────────────────────────────────────
async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    if "Ultima lectura" in texto:
        await ultima_lectura(update, context)
    elif "Historial" in texto:
        await historial(update, context)
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
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("estado", cmd_estado_bot))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))
    print("Bot iniciado. Ctrl+C para detener.")
    try:
        app.run_polling()
    finally:
        publicar_estado_bot(False)

if __name__ == "__main__":
    main()
