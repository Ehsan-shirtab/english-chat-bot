from telegram import Update
from telegram.ext import ContextTypes
from groq_helper import ask_groq

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    prompt = """
    Create a fun 3-question multiple-choice English vocabulary quiz.
    Focus on words useful in daily Canadian life, casual conversation, or general work situations.
    
    Format each question clearly with A, B, C, D options.
    Do NOT give the answers yet — just the questions.
    End with: "Reply to this message with your answers (e.g. 1-A, 2-C, 3-B) 📝"
    """

    reply = await ask_groq(prompt, use_history=False)
    await update.message.reply_text(reply, parse_mode="Markdown")
