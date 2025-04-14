import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, request

# Flask app
app = Flask(__name__)

# Налаштування Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "тут_токен_свій_встав")
CHANNEL_ID = "UCcBeq64BydUvdA-kZsITNlg"
TIKTOK_USERNAME = "top_gamer_qq"
TELEGRAM_CHANNEL = "@testbotika12"

# Telegram application
telegram_app = Application.builder().token(BOT_TOKEN).build()

# --- ФУНКЦІЇ ПЕРЕВІРКИ СТРІМІВ ---

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
        return None
    except Exception as e:
        print(f"Error checking YouTube: {str(e)}")
        return None

async def check_tiktok():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        url = f"https://www.tiktok.com/@{TIKTOK_USERNAME}/live"
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200 and '"isLive":true' in response.text:
            return f"🎥 TikTok: {url}"
        return None
    except Exception as e:
        print(f"Error checking TikTok: {str(e)}")
        return None

# --- КОМАНДИ ТА ОБРОБНИКИ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "🎥 Привіт! Я бот для перевірки стрімів на YouTube та TikTok! 🚀\n"
        "Натисни кнопку нижче, щоб дізнатися, чи є активні стріми:"
    )
    keyboard = [
        [InlineKeyboardButton("Перевірити стріми", callback_data="check_streams")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_streams":
        await query.message.reply_text("Перевіряю стріми, зачекай...")

        live_streams = []
        youtube_stream = await check_youtube()
        if youtube_stream:
            live_streams.append(youtube_stream)

        tiktok_stream = await check_tiktok()
        if tiktok_stream:
            live_streams.append(tiktok_stream)

        if live_streams:
            stream_message = "🎉 Знайдено активні стріми:\n" + "\n".join(live_streams)
            await telegram_app.bot.send_message(chat_id=TELEGRAM_CHANNEL, text=stream_message)
            await query.message.reply_text("Стріми знайдено! Я надіслав посилання в канал.")
        else:
            await query.message.reply_text("Наразі немає активних стрімів.")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button))

# --- FLASK ROUTES ---

@app.route("/webhook", methods=["POST"])
async def webhook():
    try:
        body = request.get_json(force=True)
        update = Update.de_json(body, telegram_app.bot)
        await telegram_app.process_update(update)
        return {"status": "ok"}, 200
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"error": str(e)}, 200

@app.route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}, 200

@app.route("/", methods=["GET", "HEAD"])
def root():
    return {"status": "ok"}, 200

# --- RUN ---
if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
