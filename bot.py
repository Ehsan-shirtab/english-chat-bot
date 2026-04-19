import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from groq import Groq

# Secret keys
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

client = Groq(api_key=GROQ_API_KEY)

# --- THE TRICK: A tiny dummy web server ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "English Bot is awake and listening!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)
# ------------------------------------------

# 1. NORMAL CHAT MODE (Grammar & Correction)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
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
    - Give me 2 different ways to say this that sound completely natural in an engineering environment.
    """

    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        await update.message.reply_text(chat.choices[0].message.content)
    except Exception as e:
        await update.message.reply_text("Oops, AI brain error. Please try again.")
        print(e)

# 2. QUIZ MODE (/quiz)
async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    quiz_prompt = """
    You are an expert English teacher. I am an intermediate English learner and a mechanical engineer. 
    Give me a challenging 3-question multiple-choice English vocabulary quiz focused on professional engineering and office communication. 
    Just give me the questions right now. Do not give me the answers. Wait for me to reply.
    """

    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": quiz_prompt}]
        )
        await update.message.reply_text(chat.choices[0].message.content)
    except Exception as e:
        await update.message.reply_text("Oops, AI brain error. Please try again.")
        print(e)

# 3. NEW: WORDS MODE (/words)
async def teach_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    words_prompt = """
    You are an expert English teacher. I am an intermediate English learner (native Farsi speaker) and a mechanical engineer.
    Teach me 3 new advanced, professional English vocabulary words that are highly useful in a Canadian engineering workplace.
    
    For each word, please provide:
    1. The English word and its part of speech.
    2. A simple, clear English definition.
    3. A professional example sentence related to engineering, mechatronics, or office work.
    4. The exact Farsi translation.
    
    Format the response cleanly with emojis so it is easy to read on a phone.
    """

    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": words_prompt}]
        )
        await update.message.reply_text(chat.choices[0].message.content)
    except Exception as e:
        await update.message.reply_text("Oops, AI brain error. Please try again.")
        print(e)


def main():
    # Start web server
    threading.Thread(target=run_web_server).start()

    # Start Telegram bot and add commands
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Listen for commands first
    app.add_handler(CommandHandler("quiz", start_quiz))
    app.add_handler(CommandHandler("words", teach_words))
    
    # Listen for normal text
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == '__main__':
    main()
