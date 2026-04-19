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
    Act as my personal English Tutor and Senior Engineering Mentor.
    I am an intermediate English learner (native Farsi speaker) working to improve my professional writing and speaking in a Canadian engineering workplace.

    Here is my message: "{user_text}"

    Analyze my message and reply using this EXACT format:

    🛠️ 1. Grammar & Flow Correction
    - Rewrite my exact sentence so it is grammatically correct.
    - Explain my mistake in one simple sentence.

    👔 2. Professional Alternatives
    - Give me 2 different ways to say this that sound completely natural in an engineering environment (e.g., talking to my manager or team).

    📚 3. Vocabulary Upgrade
    - Pick 1 or 2 basic words I used and teach me a more advanced, professional alternative for each.
    - Provide the exact Farsi translation for these new advanced words.

    🧠 4. Your Daily Quiz
    - Create a short "fill-in-the-blank" sentence using the new vocabulary words you just taught me. 
    - Do not give me the answer! Wait for me to reply in our next message.
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
