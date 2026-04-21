from telegram import Update
from telegram.ext import ContextTypes
from handlers.message_handler import get_mistakes
from groq_helper import ask_groq

async def show_mistakes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    user_id = update.effective_user.id
    mistakes = get_mistakes(user_id)

    if not mistakes:
        await update.message.reply_text(
            "🎉 No mistakes logged yet! Send me some sentences and I'll start tracking your patterns."
        )
        return

    mistakes_text = "\n".join(f"- {m}" for m in mistakes[-10:])

    prompt = f"""
    Here are the student's recent sentences where grammar issues were found:
    {mistakes_text}

    Analyze these and:
    1. Identify their TOP 2-3 recurring grammar patterns or mistake types.
    2. Give a short, simple explanation of each pattern.
    3. Give one easy tip to fix each pattern.

    Be encouraging and kind. Keep it simple and phone-readable.
    """

    reply = await ask_groq(prompt, use_history=False)
    await update.message.reply_text(
        f"📊 *Your Recent Mistake Patterns*\n\n{reply}",
        parse_mode="Markdown"
    )
