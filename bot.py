
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from flask import Flask, request

# Flask app
flask_app = Flask(__name__)

# Telegram settings
BOT_TOKEN = os.getenv("BOT_TOKEN", "8041256909:AAGjruzEE61q_H4R5zAwpTf53Peit37lqEg")
CHANNEL_ID = "UCcBeq64BydUvdA-kZsITNlg"
TIKTOK_USERNAME = "top_gamer_qq"
TELEGRAM_CHANNEL = "@testbotika12"

# Telegram Application
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Check YouTube stream
async def check_youtube():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        url = f"https://www.youtube.com/channel/{CHANNEL_ID}/live"
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200 and '"isLive":true' in response.text:
            title_start = response.text.find("<title>") + 7
            title_end = response.text.find("</title>")
            title = response.text[title_start:title_end].replace(" - YouTube", "")
            return f"🔴 YouTube: {title}\n{url}"
    except Exception as e:
        print(f"YouTube check error: {str(e)}")
    return None

# Check TikTok stream
async def check_tiktok():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        url = f"https://www.tiktok.com/@{TIKTOK_USERNAME}/live"
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200 and '"isLive":true' in response.text:
            return f"🎥 TikTok: {url}"
    except Exception as e:
        print(f"TikTok check error: {str(e)}")
    return None

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Перевірити стріми", callback_data="check_streams")]]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎥 Привіт! Я бот для перевірки стрімів на YouTube та TikTok!", reply_markup=markup
    )

# Button press
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_streams":
        await query.message.reply_text("Перевіряю стріми, зачекай...")

        results = []
        yt = await check_youtube()
        tt = await check_tiktok()
        if yt:
            results.append(yt)
        if tt:
            results.append(tt)

        if results:
            message = "🎉 Знайдено стріми:\n" + "\n".join(results)
            await telegram_app.bot.send_message(chat_id=TELEGRAM_CHANNEL, text=message)
            await query.message.reply_text("Стріми знайдено! Надіслав у канал.")
        else:
            await query.message.reply_text("Немає активних стрімів.")

# Add handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button))

# Flask routes
@flask_app.route("/webhook", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}

@flask_app.route("/", methods=["GET"])
def root():
    return {"status": "OK"}

@flask_app.route("/health", methods=["GET"])
def health():
    return {"status": "OK"}

# Start everything
if __name__ == "__main__":
    import asyncio

    async def run():
        await telegram_app.initialize()
        print("Telegram initialized")
        flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

    asyncio.run(run())
