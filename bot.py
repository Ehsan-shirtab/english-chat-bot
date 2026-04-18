import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from groq import Groq

# Secret keys
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

client = Groq(api_key=GROQ_API_KEY)

# --- THE TRICK: A tiny dummy web server so the cloud host keeps the bot awake ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "English Bot is awake and listening!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)
# -------------------------------------------------------------------------------

# The AI Brain
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # Show "typing..." in Telegram
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    prompt = f"""
    You are a native English speaker living in Canada. An English learner has sent you this sentence:
    "{user_text}"

    Analyze and rewrite the sentence following these strict rules:
    1. Grammar Check: Briefly and simply point out any grammatical errors.
    2. The "Real Life" Rewrite: Provide 2 different ways a real, casual person would actually say this in daily conversation. 
    3. NO AI TONGUE: Do NOT sound like a robot, a formal textbook, or an AI. Do NOT use annoying AI filler phrases like "Certainly! I can help with that." Just give the direct, human response. 
    """

    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = chat.choices[0].message.content
        await update.message.reply_text(reply)
        
    except Exception as e:
        await update.message.reply_text("Oops, AI brain error. Please try again.")
        print(e)

def main():
    # 1. Start the dummy web server in the background
    threading.Thread(target=run_web_server).start()

    # 2. Start the Telegram bot listening
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
