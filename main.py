import os
import threading
import asyncio
from flask import Flask
from telegram.ext import (
    Application, MessageHandler, CommandHandler,
    filters
)
from config import TELEGRAM_TOKEN
from handlers.commands import start, reset, set_commands, chat_mode, correct_mode
from handlers.message_handler import handle_message
from handlers.quiz_handler import start_quiz
from handlers.words_handler import teach_words, teach_topic, explain_word
from handlers.mistakes_handler import show_mistakes

# --- Keep-alive web server for Render ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "✅ English Bot (Aria) is alive and running!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)
# ----------------------------------------

def main():
    # Start keep-alive web server in background
    threading.Thread(target=run_web_server, daemon=True).start()

    # Build bot
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register all command handlers
    app.add_handler(CommandHandler("chat", chat_mode))
    app.add_handler(CommandHandler("correct", correct_mode))
    app.add_handler(CommandHandler("quiz", start_quiz))
    app.add_handler(CommandHandler("words", teach_words))
    app.add_handler(CommandHandler("mistakes", show_mistakes))
    app.add_handler(CommandHandler("topic", teach_topic))
    app.add_handler(CommandHandler("explain", explain_word))

    # Normal text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Set Telegram command menu, then start polling
    async def post_init(application):
        await set_commands(application)

    app.post_init = post_init

    print("🤖 Aria bot is starting...")
    app.run_polling()

if __name__ == '__main__':
    main()
