from telegram import Update, BotCommand
from telegram.ext import ContextTypes
from groq_helper import clear_history, set_mode


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "friend"
    await update.message.reply_text(
        f"👋 Hey {user_name}! I'm *Aria*, your English tutor and Canadian friend!\n\n"
        "Choose your mode:\n\n"
        "✏️ /correct — I fix your English only, no chat\n"
        "💬 /chat — I chat with you like a friend AND fix your English\n\n"
        "Other commands:\n"
        "📋 /quiz — Vocabulary quiz\n"
        "📖 /words — Learn 3 new words\n"
        "❌ /mistakes — See your common mistakes\n"
        "🗂️ /topic [subject] — Mini lesson\n"
        "🔍 /explain [word] — Deep dive on a word\n"
        "🔄 /reset — Clear conversation\n\n"
        "Default mode is correction. Send me any sentence to start! 🚀",
        parse_mode="Markdown"
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    clear_history(user_id)
    await update.message.reply_text(
        "🔄 Done! Cleared our conversation. Fresh start — send me anything!"
    )


async def chat_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    set_mode(user_id, "chat")
    clear_history(user_id)
    await update.message.reply_text(
        "💬 *Chat mode on!*\n\n"
        "I am your friend Aria now 😊 I will chat with you naturally "
        "AND gently fix your English in every message.\n\n"
        "Talk to me about anything — your day, life in Victoria, "
        "your plans, whatever is on your mind!\n\n"
        "Send /correct anytime to switch to correction only mode.",
        parse_mode="Markdown"
    )


async def correct_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    set_mode(user_id, "correct")
    clear_history(user_id)
    await update.message.reply_text(
        "✏️ *Correction mode on!*\n\n"
        "Send me any sentence and I will correct your English, "
        "show you natural alternatives, and give you a quick tip.\n\n"
        "Send /chat anytime to switch to friendly chat mode!",
        parse_mode="Markdown"
    )


async def set_commands(app):
    await app.bot.set_my_commands([
        BotCommand("start", "Welcome message and instructions"),
        BotCommand("correct", "Correction only mode"),
        BotCommand("chat", "Friendly chat and correction mode"),
        BotCommand("quiz", "Take a vocabulary quiz"),
        BotCommand("words", "Learn 3 new words"),
        BotCommand("mistakes", "See your common mistakes"),
        BotCommand("topic", "Mini lesson on a topic"),
        BotCommand("explain", "Deep dive on a word"),
        BotCommand("reset", "Clear conversation history"),
    ])
