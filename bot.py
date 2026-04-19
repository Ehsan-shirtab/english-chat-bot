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

# 1. NORMAL CHAT & QUIZ GRADING MODE
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    # THE TRICK: Did you swipe right to reply to the quiz?
    if update.message.reply_to_message:
        previous_text = update.message.reply_to_message.text
        prompt = f"""
        Act as my friendly English teacher. I am answering the quiz you just sent me.
        
        Here are the original questions you asked: 
        "{previous_text}"
        
        Here are my answers: 
        "{user_text}"
        
        Grade my answers using very simple, basic English. If I am wrong, explain why in one short, easy-to-understand sentence. Do not use formal or robotic language.
        """
    
    # If it's just a normal message, do the natural grammar correction
    else:
        prompt = f"""
        Act as my friendly English Tutor and Canadian friend. 
        I am an intermediate English learner (native Farsi speaker). 
        
        CRITICAL RULE: Do NOT sound like an AI, a robot, or a formal textbook. Use simple, everyday English (B1/B2 level) that is easy for me to read and speak.

        Here is my message: "{user_text}"

        Analyze my message and reply using this EXACT format:

        🛠️ 1. Grammar & Flow Correction
        - Rewrite my sentence so it is correct, but keep the words simple and natural.
        - Explain my mistake in one very simple sentence.

        👔 2. Natural Alternatives
        - Give me 2 different ways a real person would ACTUALLY say this in a quick, natural conversation (either at work or just hanging out).
        - Keep these alternatives casual, friendly, and easy to pronounce.
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
    You are an expert English teacher. I am an intermediate English learner. 
    Give me a fun, challenging 3-question multiple-choice English vocabulary quiz. 
    Focus on useful words I can use in daily conversational English, hanging out with friends, or general professional situations. 
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

# 3. WORDS MODE (/words)
async def teach_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    words_prompt = """
    You are an expert English teacher. I am an intermediate English learner (native Farsi speaker) living in Canada.
    Teach me 3 new, highly useful English vocabulary words or idioms for daily life, casual conversations, or general workplace communication.
    
    For each word, please provide:
    1. The English word/idiom.
    2. A simple, clear English definition.
    3. A natural example sentence of someone actually speaking.
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
    
    # Listen for normal text and replies
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == '__main__':
    main()
