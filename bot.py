import os
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, request

# Налаштування Flask для Webhook
app = Flask(__name__)

# Налаштування Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "8041256909:AAGjruzEE61q_H4R5zAwpTf53Peit37lqEg")
CHANNEL_ID = "UCcBeq64BydUvdA-kZsITNlg"  # YouTube Channel ID
TIKTOK_USERNAME = "top_gamer_qq"

# Ініціалізація Telegram Application
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Ініціалізуємо Application
telegram_app.initialize()

# Перевірка YouTube
async def check_youtube():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        url = f"https://www.youtube.com/channel/{CHANNEL_ID}/live"
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200 and '"isLive":true' in response.text:
            title_start = response.text.find("<title>") + 7
            title_end = response.text.find("</title>")
            title = response.text[title_start:title_end].replace(" - YouTube", "")
            return f"🔴 YouTube: {title}\n{url}"
        return None
    except Exception as e:
        print(f"Error checking YouTube: {str(e)}")
        return None

# Перевірка TikTok
async def check_tiktok():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        url = f"https://www.tiktok.com/@{TIKTOK_USERNAME}/live"
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200 and '"isLive":true' in response.text:
            return f"🎥 TikTok: {url}"
        return None
    except Exception as e:
        print(f"Error checking TikTok: {str(e)}")
        return None

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Перевірити стріми", callback_data="check_streams")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Натисни кнопку, щоб перевірити стріми:", reply_markup=reply_markup)

# Обробка натискання кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_streams":
        await query.message.reply_text("Перевіряю стріми, зачекай...")

        # Перевірка стрімів
        live_streams = []
        youtube_stream = await check_youtube()
        if youtube_stream:
            live_streams.append(youtube_stream)

        tiktok_stream = await check_tiktok()
        if tiktok_stream:
            live_streams.append(tiktok_stream)

        # Надсилаємо результат
        if live_streams:
            await query.message.reply_text("Активні стріми:\n" + "\n".join(live_streams))
        else:
            await query.message.reply_text("Наразі немає активних стрімів.")

# Додаємо обробники
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button))

# Webhook ендпоінт (синхронний)
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        body = request.get_json()
        print(f"Received webhook request: {body}")
        if not body:
            return {"status": "No JSON data"}, 200

        update = Update.de_json(body, telegram_app.bot)
        if update:
            # Використовуємо run_async для асинхронної обробки
            telegram_app.run_async(telegram_app.process_update(update))
            print("Update processed successfully")
        else:
            print("Invalid update data")

        return {"status": "OK"}, 200
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return {"error": str(e)}, 200

# Health check для UptimeRobot
@app.route('/health', methods=['GET'])
def health():
    return {"status": "OK"}, 200

# Запускаємо Flask
if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
