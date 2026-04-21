from telegram import Update, BotCommand
from telegram.ext import ContextTypes
from groq_helper import clear_history

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "friend"
    await update.message.reply_text(
        f"👋 Hey {user_name}! I'm *Aria*, your English tutor and Canadian friend!\n\n"
        "Here's what I can do for you:\n\n"
        "💬 *Just send me any message* — I'll fix your grammar and teach you natural alternatives.\n\n"
        "📋 */quiz* — Take a 3-question vocabulary quiz.\n"
        "📖 */words* — Learn 3 new useful words or idioms.\n"
        "❌ */mistakes* — See your most common grammar mistakes.\n"
        "🗂️ */topic [subject]* — Get a mini-lesson (e.g. /topic job interview).\n"
        "🔍 */explain [word]* — Deep dive on any word.\n"
        "🔄 */reset* — Clear our conversation and start fresh.\n\n"
        "Let's start! Send me any sentence 🚀",
        parse_mode="Markdown"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    clear_history(user_id)
    await update.message.reply_text(
        "🔄 Done! I've cleared our conversation history. Fresh start — send me anything!"
    )

async def set_commands(app):
    """Register command list shown in Telegram menu."""
    await app.bot.set_my_commands([
        BotCommand("start", "Welcome message & instructions"),
        BotCommand("quiz", "Take a vocabulary quiz"),
        BotCommand("words", "Learn 3 new words/idioms"),
        BotCommand("mistakes", "See your common mistakes"),
        BotCommand("topic", "Mini-lesson on a topic"),
        BotCommand("explain", "Deep-dive on a word"),
        BotCommand("reset", "Clear conversation history"),
    ])
